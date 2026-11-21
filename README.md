<h1 align="center">🦾 LeGUI</h1>

<p align="center">
  <b>A self-hosted graphical interface for <a href="https://github.com/huggingface/lerobot">LeRobot</a> — built on top of Hugging Face's <a href="https://github.com/huggingface/leLab">LeLab</a>.</b>
</p>

<div align="center">

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](./LICENSE)
[![Upstream](https://img.shields.io/badge/upstream-huggingface%2FleLab-FFD21E)](https://github.com/huggingface/leLab)
[📖 文档](https://openpilotcc.github.io/leLab/)

</div>

**LeGUI** is an independently maintained fork of [LeLab](https://github.com/huggingface/leLab), Hugging Face's web app that puts the full LeRobot workflow — calibrate, teleoperate, record, train, replay — into a single browser UI. All credit for the original design and implementation goes to the LeLab team at Hugging Face; this fork carries that work forward with fixes and features for self-hosted setups, and tracks the latest LeRobot release.

> **License note:** LeGUI is distributed under the same [Apache License 2.0](./LICENSE) as the original LeLab. The original code is Copyright 2025 The HuggingFace Inc. team; modifications in this fork are made under the same license.

## What this fork changes

- **Works over plain-HTTP LAN access** — the full story, end to end:
  - camera previews are streamed **from the backend as MJPEG video** (`/camera-preview`, `/camera-feed`), so no browser camera permissions, no HTTPS and no `localhost` are needed to see your cameras on any device;
  - the frontend survives insecure contexts (`crypto.randomUUID` fallback, same-origin API default);
  - a `--host` flag makes the server reachable from other machines.
- **Chinese localization** — a language switcher in the top bar (English / 中文), persisted per browser.
- **Calibration flow** aligned with lerobot v0.7 semantics: an explicit *confirm the middle position* step (that pose becomes the zero point, so leader and follower line up in teleoperation), and the continuous-rotation `wrist_roll` gets the full encoder span instead of a recorded range.
- **Teleoperation camera streams** — the follower's cameras stream live during a session.
- **Launcher flags** — `--host`, `--port`, `--https`, plus robust stop (`--stop --port`).

## Tracks the latest LeRobot

LeGUI pins LeRobot to the latest upstream release tag (currently **`v0.7.0`**, see [pyproject.toml](pyproject.toml)) and bumps the pin as new LeRobot versions come out. The pinned API is what the calibration and recording flows are written against — upgrading LeRobot is done through a LeGUI bump, not by mixing versions.

## Quick Start

```bash
uv tool install --force --with-executables-from huggingface_hub \
  git+https://github.com/openpilotcc/leLab.git
```

Then:

```bash
lelab --host 0.0.0.0
```

A page opens automatically; from other devices open `http://<server-ip>:8000`. The in-app *Update now* button reinstalls this same branch (updates are checked against this repository).

### Custom host and port

By default LeGUI serves the UI and API on `127.0.0.1:8000`, reachable only from the machine it runs on. Two flags change that:

```bash
lelab --host 0.0.0.0              # also listen on the network, e.g. for a laptop or tablet next to the arm
lelab --port 9000                 # serve on a different port
lelab --host 0.0.0.0 --port 9000  # both at once
```

Then open `http://<server-ip>:<port>` from any device on the same network. `lelab --stop` frees the ports again; pass `--port` too if you started on a custom port. In `--dev` mode, `--host` applies to the Vite dev server (`:8080`) as well, and `--port` selects the backend port that the dev frontend talks to.

## What you can do

<div align="center">
  <table>
    <tr>
      <td>🎯 <b>Calibrate</b></td>
      <td>Guided web flow for both arms — middle-position zero point, full-range recording, no keyboard prompts.</td>
    </tr>
    <tr>
      <td>🕹️ <b>Teleoperate</b></td>
      <td>Move the leader, the follower mirrors it. Live joint streaming and live camera previews over plain HTTP.</td>
    </tr>
    <tr>
      <td>📹 <b>Record</b></td>
      <td>Capture episodes into a LeRobotDataset, with cameras.</td>
    </tr>
    <tr>
      <td>🔎 <b>Browse</b></td>
      <td>Watch the episodes of a dataset on disk — every camera, frame by frame, with a joint-motion trace. No upload required.</td>
    </tr>
    <tr>
      <td>🧠 <b>Train</b></td>
      <td>Kick off a LeRobot training job (SmolVLA, ACT, ...), watch logs live.</td>
    </tr>
    <tr>
      <td>🤖 <b>Run inference</b></td>
      <td>Execute a trained policy on the follower.</td>
    </tr>
    <tr>
      <td>⏪ <b>Replay</b></td>
      <td>Re-run any recorded episode.</td>
    </tr>
    <tr>
      <td>☁️ <b>Upload</b></td>
      <td>Push your dataset to the <a href="https://huggingface.co/">Hugging Face Hub</a> in one click.</td>
    </tr>
  </table>
</div>

## Camera rotation

If a camera is mounted upside down or sideways, select its **Rotation** in the camera setup on the Calibration page.

## Resources

- **[LeRobot](https://github.com/huggingface/lerobot):** the underlying library — go here for everything beyond the UI.
- **[LeLab](https://github.com/huggingface/leLab):** the upstream project this fork is built on — its releases, ideas and community are the source of this work.

## Contribute

PRs welcome. Hot-reload mode for working on the code:

```bash
lelab --dev
```

Vite on `:8080`, uvicorn `--reload` on `:8000`. Installing LeGUI builds the frontend bundle, so PRs never include `frontend/dist`.
