# LeGUI — LeRobot 图形界面

**LeGUI** 是一个自主维护的 [LeLab](https://github.com/huggingface/leLab)（Hugging Face 官方 LeRobot 图形界面）分支，把 LeRobot 的完整工作流——校准、遥操作、录制数据集、训练、回放——装进一个浏览器界面。插上机械臂、打开网页即可开始，无需命令行 gymnastics。

> **出处声明**：本项目基于 Hugging Face 的 [LeLab](https://github.com/huggingface/leLab) 分支开发，原项目的设计与实现版权归 Hugging Face LeLab 团队所有。LeGUI 在其基础上为自托管场景做了增强，详见 [出处与许可证](about.md)。

## 为什么选 LeGUI（本分支的增强）

- **纯 HTTP 局域网全功能**：相机画面由后端采集并以 MJPEG 视频流推给浏览器，不需要 HTTPS、不需要 `localhost`、不需要任何浏览器权限弹窗——局域网内任何设备（电脑/平板/手机浏览器）打开即用。
- **中文界面**：顶栏一键切换 中文 / English，按浏览器语言自动选择。
- **校准流程对齐 lerobot v0.7 语义**：明确的「确认中位姿势」步骤（该姿势成为零点，保证主臂与从臂遥操作姿态对齐）；连续旋转关节 `wrist_roll` 写入全编码器行程，不会被校准范围钳制。
- **遥操作实时相机**：会话期间从臂相机以视频流实时显示。
- **网络参数齐备**：`--host` / `--port` / `--https` / `--stop` 一应俱全。

## 跟踪最新 LeRobot

LeGUI 将 LeRobot 锁定在最新上游发布 tag（当前 **v0.7.0**）。校准与录制流程都是针对该版本 API 编写的；LeRobot 新版本发布后，LeGUI 会随之升级 pin，保证两者口径一致。

## 快速开始

```bash
uv tool install --force --with-executables-from huggingface_hub \
  git+https://github.com/openpilotcc/LeGUI.git
```

启动（局域网可访问）：

```bash
lelab --host 0.0.0.0
```

自动打开浏览器后即可使用；其他设备访问 `http://<服务器IP>:8000`。详细的安装、升级与局域网配置见 [安装与升级](install.md) 与 [局域网访问与更新](guide/network.md)。

## 下一步

- [安装与升级](install.md) —— 一条命令装好 LeGUI + LeRobot
- [校准机械臂](guide/calibration.md) —— 首次使用必做
- [录制与数据集](guide/record.md) —— 采集你的第一份数据集
- [训练策略](guide/train.md) —— 训练 SmolVLA / ACT
