import i18n from "@/i18n";
import React, { useCallback, useEffect, useRef, useState } from "react";
import { cameraPreviewGeometry, CameraRotation } from "@/lib/cameraConfig";

interface BackendCameraFeedProps {
  // Complete MJPEG stream URL, e.g. {baseUrl}/camera-preview/0.
  src: string;
  /** Native capture dimensions, used for the rotation geometry. */
  width: number;
  height: number;
  rotation: CameraRotation;
  /** Optional saved reference frame shown as a ghost over the live feed. */
  ghostSrc?: string;
  ghostOpacity?: number;
  /** Name badge rendered in the corner. */
  name: string;
}

// Renders one camera as a backend MJPEG stream in a plain <img> — the browser
// never touches the camera API, so previews work over plain-HTTP LAN access,
// in embedded webviews and without any permission prompt. The browser renders
// a `multipart/x-mixed-replace` response natively; if the stream errors before
// frames flow (device busy, camera warming up), retry with a cache-busting
// key after a delay.
const BackendCameraFeed: React.FC<BackendCameraFeedProps> = ({
  src: streamUrl,
  width,
  height,
  rotation,
  ghostSrc,
  ghostOpacity,
  name,
}) => {
  const [reloadKey, setReloadKey] = useState(0);
  const [hasError, setHasError] = useState(false);
  const retryRef = useRef<number | null>(null);

  useEffect(() => {
    return () => {
      if (retryRef.current) window.clearTimeout(retryRef.current);
    };
  }, []);

  const handleError = useCallback(() => {
    setHasError(true);
    if (retryRef.current) window.clearTimeout(retryRef.current);
    retryRef.current = window.setTimeout(() => {
      setHasError(false);
      setReloadKey((k) => k + 1);
    }, 1500);
  }, []);

  // Reset the error state when the stream source changes.
  useEffect(() => {
    setHasError(false);
  }, [streamUrl]);

  const geometry = cameraPreviewGeometry(width, height, rotation);

  return (
    <div
      className="relative w-full overflow-hidden rounded-lg border border-gray-800 bg-black"
      style={{ aspectRatio: geometry.aspectRatio }}
    >
      {hasError ? (
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-xs text-gray-500">{i18n.t("Connecting feed…")}</span>
        </div>
      ) : (
        <img
          src={`${streamUrl}?k=${reloadKey}`}
          alt={`${name} live feed`}
          onError={handleError}
          style={geometry.videoStyle}
          className="absolute inset-0"
        />
      )}
      {ghostSrc && !hasError && (
        <img
          src={ghostSrc}
          alt=""
          aria-hidden
          className="absolute inset-0 pointer-events-none"
          style={{ ...geometry.videoStyle, opacity: ghostOpacity ?? 0.35 }}
        />
      )}
      <span className="absolute bottom-1 left-1 px-1.5 py-0.5 rounded bg-black/60 text-xs text-gray-200">
        {name}
      </span>
    </div>
  );
};

export default BackendCameraFeed;
