# 局域网访问与更新

## 为什么要 --host

默认 `lelab` 只监听 `127.0.0.1`（仅本机可访问）。想在局域网内其他设备（平板、笔记本、手机浏览器）上使用，启动时加 `--host`：

```bash
lelab --host 0.0.0.0
```

其他设备访问 `http://<服务器IP>:8000`。自定义端口与组合用法：

```bash
lelab --host 0.0.0.0 --port 9000   # 同时自定义 IP 绑定与端口
lelab --stop --port 9000           # 停止自定义端口的服务实例
lelab --dev                        # 开发模式（Vite :8080 + 后端 :8000）
```

## 相机画面在局域网也能看

LeGUI 的相机预览全部由**后端采集、MJPEG 视频流推给浏览器**——浏览器不需要摄像头权限、不需要 HTTPS、不需要 localhost。这正是本分支与上游的核心差异之一：插电连网，打开就用。

!!! note "纯 HTTP 下不可用的功能"

    浏览器的**语音识别**（语音指令）仍要求安全上下文，纯 HTTP 访问时不可用——任务描述手动输入即可，录制与预览不受影响。

## HTTPS（可选）

只有两种场景需要 HTTPS：浏览器语音指令，或某些内网策略强制要求。LeGUI 支持 `--https` 一键开启（自动生成自签名证书，SAN 覆盖服务器所有网卡 IP）：

```bash
lelab --https --host 0.0.0.0
```

浏览器首次访问会提示证书不受信任——点「高级 → 继续前往」一次即可（证书有效期 825 天，存放于 `~/.cache/huggingface/lerobot/certs/`）。自签名证书只影响浏览器信任提示，不影响功能。也可以用 `--ssl-certfile/--ssl-keyfile` 指定正规证书。

## 应用内更新

页面右上角的更新检查会对比本仓库（openpilotcc/leLab）的提交：

- 显示 **有新版本可用** 时，点 **Update now** 或复制页面给出的命令执行——它重装的是**当前发布分支**（锁定 `@feat/chinese-i18n`），不会丢失本分支的任何增强；
- 更新完成后重启服务（`lelab --stop` 再启动）。

也可以随时手动执行：

```bash
uv tool install --force --with-executables-from huggingface_hub \
  git+https://github.com/openpilotcc/leLab.git
lelab --host 0.0.0.0
```

## 防火墙

如果其他设备仍无法访问，检查服务器防火墙是否放行了端口：

```bash
sudo ufw status          # Ubuntu 常见为 ufw
sudo ufw allow 8000/tcp  # 放行示例
```
