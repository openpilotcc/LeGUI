# Copyright 2025 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""On-demand MJPEG camera previews for browsers.

Browsers expose getUserMedia only in secure contexts, so a browser opened
over plain HTTP on a LAN IP cannot touch the camera at all. Instead the
backend opens the camera with cv2 and streams multipart JPEG frames; the
frontend just renders an <img>, needing no browser camera API, no
permissions and no HTTPS.

Two stream sources live here:

- `index_frames(index)`: opens any cv2 camera index on demand, for the
  calibration page, camera binding dropdowns and inference setup — places
  where no robot session exists to hold the device. A worker thread per
  index keeps the device open while at least one viewer is connected and
  releases it after a short idle timeout, so recording can claim the
  camera exclusively again.
- `teleop_camera_feed_frames(cam_key)`: mirrors `record.camera_feed_frames`
  for teleoperation, peeking the teleop robot's `read_latest()` frame
  buffer so the teleoperation page previews work the same way as the
  recording page's.

Workers import cv2 lazily so importing this module stays cheap.
"""

from __future__ import annotations

import logging
import threading
import time

logger = logging.getLogger(__name__)

FPS = 10.0
# How long a worker keeps an opened device around after its last viewer
# disconnected — short, so recording can claim the camera exclusively again.
IDLE_RELEASE_SECONDS = 5.0


class _IndexWorker:
    """Opens one cv2 camera index and keeps the latest JPEG frame ready.

    Opening can transiently fail while another claimant (the recorder, a
    sibling camera worker on the same USB controller) holds the bus, so the
    run loop retries the open every couple of seconds and keeps the stream
    alive with the rendered error notice — once the device becomes free the
    same stream silently turns into live frames. The worker exits only after
    IDLE_RELEASE_SECONDS with no viewers, releasing the device.
    """

    def __init__(self, index: int) -> None:
        self.index = index
        self.lock = threading.Lock()
        self.jpeg: bytes | None = None
        self.error: str | None = None
        self.viewers = 0
        # Monotonic timestamp of the last viewer disconnect; while any viewer
        # is connected (`viewers > 0`) the idle check never fires.
        self.last_viewer_gone = time.monotonic()
        self.thread = threading.Thread(target=self._run, daemon=True)

    def start(self) -> None:
        self.thread.start()

    def frame(self) -> bytes | None:
        with self.lock:
            return self.jpeg

    def error_text(self) -> str | None:
        with self.lock:
            return self.error

    def _run(self) -> None:
        import cv2

        cap = None
        try:
            while True:
                with self.lock:
                    idle = self.viewers == 0
                if idle and time.monotonic() - self.last_viewer_gone > IDLE_RELEASE_SECONDS:
                    break

                if cap is None or not cap.isOpened():
                    if cap is not None:
                        cap.release()
                        cap = None
                    cap = cv2.VideoCapture(self.index)
                    if not cap.isOpened():
                        cap.release()
                        cap = None
                        with self.lock:
                            self.error = "camera unavailable"
                        time.sleep(2.0)
                        continue
                    with self.lock:
                        self.error = None

                ok, frame = cap.read()
                if ok:
                    ok, buf = cv2.imencode(".jpg", frame)
                    if ok:
                        with self.lock:
                            self.jpeg = buf.tobytes()
                            self.error = None
                time.sleep(1.0 / FPS)
        finally:
            if cap is not None:
                cap.release()

    def alive(self) -> bool:
        return self.thread.is_alive()


class PreviewManager:
    """Lazily starts one `_IndexWorker` per camera index."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._workers: dict[int, _IndexWorker] = {}

    def frames(self, index: int, fps: float = FPS):
        """Yield multipart-MJPEG chunks of one camera's latest frames.

        Registers a viewer for the worker's lifetime so the device stays
        open, and unregisters in `finally` whichever way the client goes.
        """
        with self._lock:
            worker = self._workers.get(index)
            if worker is None or not worker.alive():
                worker = _IndexWorker(index)
                self._workers[index] = worker
                worker.start()
            worker.viewers += 1
        try:
            # While the worker retries the device open, keep the stream alive
            # by re-rendering the error notice at a slow rate — an <img> shows
            # the notice now and silently turns into live frames once the
            # device becomes available. Live frames flow at `fps`.
            while True:
                if not worker.alive():
                    # Worker exited for its own reason (idle release): end the
                    # stream so the frontend's retry loop takes over.
                    break
                frame = worker.frame()
                if frame is not None:
                    yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
                    time.sleep(1.0 / fps)
                else:
                    notice = worker.error_text() or "camera unavailable"
                    yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + _error_jpeg(notice) + b"\r\n")
                    time.sleep(1.0)
        finally:
            with self._lock:
                worker.viewers -= 1
                worker.last_viewer_gone = time.monotonic()


def _error_jpeg(text: str) -> bytes:
    """Render a one-line error message as a JPEG so <img> previews show why."""
    import cv2
    import numpy as np

    img = np.zeros((240, 426, 3), dtype=np.uint8)
    cv2.putText(img, text, (16, 124), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1, cv2.LINE_AA)
    ok, buf = cv2.imencode(".jpg", img)
    return buf.tobytes() if ok else b""


manager = PreviewManager()


def index_frames(index: int, fps: float = FPS):
    """Multipart generator for the on-demand preview of a cv2 camera index."""
    return manager.frames(index, fps)


def teleop_camera_feed_frames(cam_key: str, fps: float = 15.0):
    """Yield multipart-MJPEG chunks of one teleop robot camera's latest frames.

    Mirrors `record.camera_feed_frames`, reading the teleop robot's
    lock-protected `read_latest()` buffer instead — so the teleoperation page
    can preview configured cameras while its session is live. Streams only
    while the session is live and the named camera exists; ends cleanly
    otherwise so the browser <img> stops.
    """
    import cv2

    from lelab import teleoperate as _teleoperate

    interval = 1.0 / fps
    # The session sets current_robot only after the robot connects; give it a
    # moment to appear, same warm-up window as the recording feed.
    deadline = time.time() + 15.0
    while _teleoperate.teleoperation_active and _teleoperate.current_robot is None and time.time() < deadline:
        time.sleep(0.1)

    while _teleoperate.teleoperation_active:
        robot = _teleoperate.current_robot
        if robot is None:
            break
        cam = robot.cameras.get(cam_key)
        if cam is None:
            break
        try:
            frame = cam.read_latest()
        except (TimeoutError, RuntimeError):
            time.sleep(interval)
            continue
        except Exception as e:
            logger.warning("teleop camera-feed %s: unexpected read error: %s", cam_key, e)
            break

        bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        ok, buf = cv2.imencode(".jpg", bgr)
        if not ok:
            time.sleep(interval)
            continue
        yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + buf.tobytes() + b"\r\n"
        time.sleep(interval)
