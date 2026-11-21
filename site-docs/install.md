# 安装与升级

## 前置条件

- 一台 Linux 电脑（与机械臂同一局域网），装有 [uv](https://docs.astral.sh/uv/)（没有就先装）：

  ``` bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

- 机械臂（SO-101 主臂 + 从臂）通过 USB 串口连接到这台电脑，**电源已接通**。

## 安装

一条命令同时装好 LeGUI 与 LeRobot（uv 会自动构建前端界面）：

``` bash
uv tool install --force --with-executables-from huggingface_hub \
  git+https://github.com/openpilotcc/leLab.git
```

说明：

- 发布内容已在默认分支 main 上，直接安装即可。
- `--with-executables-from huggingface_hub` 会顺带装好 `hf` 命令（登录 Hugging Face、上传数据集要用）。

## 启动与停止

``` bash
lelab --host 0.0.0.0    # 启动，本机浏览器自动打开；其他设备访问 http://<服务器IP>:8000
lelab --stop            # 停止并释放端口
```

更多参数（自定义端口、HTTPS、开发模式）见 [局域网访问与更新](guide/network.md)。

## 升级

发布分支有新提交后，重跑安装命令（加 `--force`）：

``` bash
uv tool install --force --with-executables-from huggingface_hub \
  git+https://github.com/openpilotcc/leLab.git
```

然后重启服务即可。也可以直接使用页面右上角的「检查更新」——应用内的 **Update now** 按钮会重装同一个发布分支，不会覆盖你的本地增强（它会锁定安装时使用的分支名）。

!!! note "升级会重建前端"

    uv 安装时会自动执行前端构建（含中文翻译），无需手工操作。

## 故障排查

- **安装时报 GitHub 连接错误（TLS/超时）**：网络抖动，重跑几次即可。
- **启动报端口被占用**：先 `lelab --stop`，再启动。
- **页面打开但连接不上后端**：确认用 `--host 0.0.0.0` 启动，且访问地址与服务器在同一网段。
