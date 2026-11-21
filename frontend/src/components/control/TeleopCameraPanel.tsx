import i18n from "@/i18n";
import React, { useState } from "react";
import { RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { useRobots } from "@/hooks/useRobots";
import { useApi } from "@/contexts/ApiContext";
import BackendCameraFeed from "@/components/control/BackendCameraFeed";

/**
 * Optional live camera panel for the teleoperation page. Off by default so we
 * never call getUserMedia just by landing on the page (same consent pattern as
 * the calibration camera toggle). Teleoperation opens no cv2 cameras, so the
 * browser can stream them directly while the arm runs.
 *
 * A strict mirror of the selected robot's configured cameras: one live feed per
 * camera on the robot record (e.g. "wrist_cam", "webcam"), stacked vertically.
 * If the robot has none configured it shows nothing — teleop never surfaces a
 * device that wasn't deliberately added to the robot.
 */
const TeleopCameraPanel: React.FC = () => {
  const [enabled, setEnabled] = useState(false);
  // Bumped by the retry button to remount the feeds (a fresh stream attempt)
  // — useful if a camera was unplugged and reconnected.
  const [reloadKey, setReloadKey] = useState(0);
  const { baseUrl } = useApi();
  const { selectedRecord, isLoading: robotsLoading } = useRobots();

  // Feeds come solely from the robot's configured cameras, streamed by the
  // backend from their cv2 indices (see /camera-feed), so they work over
  // plain-HTTP LAN access where browsers have no camera API. A configured
  // camera whose device is currently absent still shows (name + failed-preview
  // placeholder), so the user can tell it's expected but not detected.
  const configured = selectedRecord?.cameras ?? [];
  const feeds = configured.map((c) => ({
    key: c.id,
    name: c.name,
    index: c.camera_index,
    rotation: c.rotation,
    width: c.width,
    height: c.height,
  }));

  return (
    <div className="bg-gray-900 rounded-lg p-4 flex flex-col gap-4 h-full">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-medium text-gray-200">{i18n.t("Cameras")}</h2>
        <div className="flex items-center gap-2">
          {enabled && feeds.length > 0 && (
            <Button
              type="button"
              variant="ghost"
              size="icon"
              onClick={() => setReloadKey((k) => k + 1)}
              className="h-9 w-9 text-gray-400 hover:text-white flex-shrink-0"
              title={i18n.t("Retry camera feeds (e.g. after reconnecting a camera)")}
              aria-label={i18n.t("Retry camera feeds")}
            >
              <RefreshCw className="w-4 h-4" />
            </Button>
          )}
          <Label htmlFor="teleop-camera-toggle" className="text-sm text-gray-400">
            {enabled ? "On" : i18n.t("Off")}
          </Label>
          <Switch
            id="teleop-camera-toggle"
            checked={enabled}
            onCheckedChange={setEnabled}
          />
        </div>
      </div>

      {enabled ? (
        feeds.length > 0 ? (
          <div className="flex flex-col gap-3 overflow-y-auto">
            {feeds.map((feed) => (
              <BackendCameraFeed
                key={`${feed.key}:${reloadKey}`}
                src={`${baseUrl}/camera-feed/${encodeURIComponent(feed.name)}`}
                name={feed.name}
                rotation={feed.rotation}
                width={feed.width}
                height={feed.height}
              />
            ))}
          </div>
        ) : (
          <p className="text-sm text-gray-500">
            {robotsLoading
              ? i18n.t("Loading robot...")
              : i18n.t("No cameras configured for this robot. Add them during calibration to see live feeds here.")}
          </p>
        )
      ) : (
        <p className="text-sm text-gray-500">
          {i18n.t("Turn on to watch your cameras while you teleoperate.")}</p>
      )}
    </div>
  );
};

export default TeleopCameraPanel;
