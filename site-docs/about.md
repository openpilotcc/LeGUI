# 出处与许可证

## 出处

**LeGUI** 基于 Hugging Face 官方的 **[LeLab](https://github.com/huggingface/leLab)** 项目分支开发。LeLab 是 LeRobot 的官方图形界面，由 2025 年 LeRobot Worldwide Hackathon 的 LeLab 团队首创，现由 Hugging Face 的 LeRobot 团队维护。

LeGUI 继承了 LeLab 的全部核心设计与实现——校准、遥操作、录制、训练、回放的完整 web 工作流，以及精心打磨的交互体验。对原项目团队，本 fork 致以诚挚感谢。

## 与上游的关系

- 本分支曾向上游提交过多项修复（局域网 HTTP 支持、校准流程、CLI 参数），目前自主维护、独立演进；
- 会持续关注上游的更新与改进，有价值的变更会合入本分支；
- LeRobot 版本跟随上游最新发布 tag（见 [首页](index.md)）。

## 许可证

本项目与上游 LeLab 相同，采用 **Apache License 2.0** 发布：

- 原始代码版权归 **The HuggingFace Inc. team** 所有（见各源文件的版权头）；
- 本分支的修改同样以 Apache License 2.0 发布；
- [LICENSE](https://github.com/openpilotcc/leLab/blob/feat/chinese-i18n/LICENSE) 文件完整保留。

## 本分支相对上游的主要增强

- 纯 HTTP 局域网全功能支持（后端 MJPEG 相机流、安全上下文兼容、同源 API 默认值）
- 中文界面（i18n 框架 + 全量翻译 + 语言切换器）
- 校准流程对齐 lerobot v0.7 语义（中位确认零点、wrist_roll 全编码器）
- 校准错误信息完整显示到前端
- 启动器 `--host` / `--port` / `--https` / `--stop --port`
- 遥操作会话相机实时流
- 应用内更新锁定发布分支
