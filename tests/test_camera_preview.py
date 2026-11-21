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
"""Tests for the on-demand MJPEG camera preview manager.

The manager runs a worker thread per camera index; these tests stub `cv2`
with fakes so no device is touched.
"""

from __future__ import annotations

import sys
import threading
import time
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest


class FakeCapture:
    """Stands in for cv2.VideoCapture: yields N frames, then blocks."""

    def __init__(self, device_index: int, frames: int = 5, opened: bool = True):
        self.device_index = device_index
        self.opened = opened
        self.remaining = frames
        self.released = False
        self._cond = threading.Condition()

    def isOpened(self) -> bool:  # noqa: N802 - mirrors cv2's API
        return self.opened

    def read(self):
        with self._cond:
            if self.remaining > 0:
                self.remaining -= 1
                return True, f"frame-{self.device_index}-{self.remaining}"
            # Blocks like a real capture would between frames; the worker's
            # idle timeout is what ends the test deterministically.
            self._cond.wait(timeout=0.05)
            return False, None

    def release(self) -> None:
        self.released = True


@pytest.fixture()
def fake_cv2(monkeypatch: pytest.MonkeyPatch):
    """Install a fake cv2 module whose VideoCapture yields a few frames."""
    captures: list[FakeCapture] = []
    holder = {"overlay_text": None}

    def VideoCapture(index: int) -> FakeCapture:  # noqa: N802 - mirrors cv2's API
        cap = FakeCapture(index)
        captures.append(cap)
        return cap

    def imencode(_ext, frame):
        label = holder["overlay_text"] if holder["overlay_text"] else frame
        return (True, MagicMock(tobytes=lambda: f"jpg:{label}".encode()))

    def cvt_color(frame, _code):
        return frame

    def put_text(_img, text, *_args, **_kwargs):
        holder["overlay_text"] = text

    fake = SimpleNamespace(
        VideoCapture=VideoCapture,
        imencode=imencode,
        cvtColor=cvt_color,
        putText=put_text,
        FONT_HERSHEY_SIMPLEX=0,
        LINE_AA=1,
    )
    fake.holder = holder
    monkeypatch.setitem(sys.modules, "cv2", fake)
    return SimpleNamespace(fake=fake, captures=captures)


def _drain(generator, expected_chunks: int, timeout: float = 5.0) -> list[bytes]:
    """Pull chunks from the MJPEG generator with a wall-clock deadline."""
    chunks: list[bytes] = []
    deadline = time.monotonic() + timeout
    for chunk in generator:
        chunks.append(chunk)
        if len(chunks) >= expected_chunks or time.monotonic() > deadline:
            generator.close()
            break
    return chunks


def test_index_frames_yields_mjpeg_chunks(fake_cv2) -> None:
    from lelab import camera_preview

    gen = camera_preview.index_frames(0)
    chunks = _drain(gen, expected_chunks=3)

    assert len(chunks) == 3
    assert all(chunk.startswith(b"--frame\r\nContent-Type: image/jpeg\r\n\r\n") for chunk in chunks)
    assert all(b"jpg:frame-0" in chunk for chunk in chunks)
    assert len(fake_cv2.captures) == 1


def test_worker_releases_camera_after_viewers_leave(fake_cv2, monkeypatch: pytest.MonkeyPatch) -> None:
    from lelab import camera_preview

    monkeypatch.setattr(camera_preview, "IDLE_RELEASE_SECONDS", 0.2)
    gen = camera_preview.index_frames(1)
    next(gen, None)  # start the worker, grab one frame if available
    gen.close()

    captures = fake_cv2.captures
    deadline = time.monotonic() + 3.0
    while time.monotonic() < deadline:
        if captures and captures[0].released:
            break
        time.sleep(0.05)

    assert captures and captures[0].released


def test_dead_worker_ends_the_stream_immediately(fake_cv2, monkeypatch: pytest.MonkeyPatch) -> None:
    from lelab import camera_preview

    def dead_worker(_index: int):
        return SimpleNamespace(
            frame=lambda: None,
            alive=lambda: False,
            viewers=0,
            start=lambda: None,
            last_viewer_gone=time.monotonic(),
        )

    monkeypatch.setattr(camera_preview, "_IndexWorker", dead_worker)
    gen = camera_preview.index_frames(7)

    # The worker already exited, so the generator ends without emitting
    # anything and the frontend's retry loop takes over.
    assert list(gen) == []


def test_error_notice_streams_while_the_worker_retries(fake_cv2, monkeypatch: pytest.MonkeyPatch) -> None:
    from lelab import camera_preview

    def retrying_worker(_index: int):
        return SimpleNamespace(
            frame=lambda: None,
            alive=lambda: True,
            error_text=lambda: "camera unavailable",
            viewers=0,
            start=lambda: None,
            last_viewer_gone=time.monotonic(),
        )

    monkeypatch.setattr(camera_preview, "_IndexWorker", retrying_worker)
    gen = camera_preview.index_frames(7)
    chunks = _drain(gen, expected_chunks=2)

    # The stream stays alive, re-rendering the notice so the <img> shows why
    # no live frames are flowing yet.
    assert len(chunks) == 2
    assert all(b"camera unavailable" in chunk for chunk in chunks)


def test_second_viewer_reuses_the_same_worker(fake_cv2) -> None:
    from lelab import camera_preview

    gen1 = camera_preview.index_frames(3)
    next(gen1, None)
    gen2 = camera_preview.index_frames(3)
    next(gen2, None)

    assert len(fake_cv2.captures) == 1

    gen1.close()
    gen2.close()
