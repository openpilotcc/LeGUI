/**
 * Web camera APIs (`navigator.mediaDevices`) are exposed only in secure
 * contexts (HTTPS or localhost). On plain-HTTP LAN access — e.g.
 * http://<host-ip>:8000 — the object is `undefined`, and even
 * `addEventListener` on it throws, which used to blank out whole pages.
 * Every camera code path guards on this first and degrades to a friendly
 * notice instead.
 */
export const mediaDevicesAvailable = (): boolean =>
  typeof navigator !== "undefined" && !!navigator.mediaDevices;

/** Natural i18n key of the user-facing explanation for the missing API. */
export const CAMERA_SECURE_CONTEXT_KEY =
  "Camera access needs HTTPS or localhost. Open LeLab via http://localhost:8000, or set up HTTPS (see HTTPS_SETUP.md).";
