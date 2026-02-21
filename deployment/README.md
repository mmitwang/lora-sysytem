# 温振监控系统部署指南

## 系统要求
- Ubuntu 22.04 LTS
- 至少 2GB 内存
- 至少 20GB 磁盘空间
- 互联网连接（用于下载依赖和代码）

## 部署方式

### 方式一：Docker容器部署（推荐）
- **Docker容器部署**：使用Docker容器隔离运行环境，避免与系统其他依赖冲突
- **一键部署**：自动化脚本，无需手动配置
- **容器管理**：使用Docker管理容器，支持自动重启
- **设备映射**：串口设备映射到容器内，支持硬件通信

### 方式二：虚拟环境部署
- **虚拟环境部署**：使用独立的Python虚拟环境，避免与系统其他Python依赖冲突
- **一键部署**：自动化脚本，无需手动配置
- **服务管理**：使用systemd管理服务，支持自动启动和重启
- **完整依赖**：自动安装所有必要的系统和Python依赖

## 部署步骤

### 1. 下载部署文件
将 `deployment.tar.gz` 上传到 Ubuntu 22.04 服务器上，然后解压：

```bash
# 解压部署包
tar -xzvf deployment.tar.gz

# 进入部署目录
cd deployment
```

### 2. Docker容器部署（推荐）

```bash
# 赋予脚本执行权限
chmod +x docker-deploy.sh

# 运行Docker部署脚本（必须使用root权限）
sudo ./docker-deploy.sh
```

### 3. 虚拟环境部署

```bash
# 赋予脚本执行权限
chmod +x deploy.sh

# 运行部署脚本（必须使用root权限）
sudo ./deploy.sh
```

### 4. 等待部署完成

#### Docker部署步骤：
1. 检查并安装Docker（如果未安装）
2. 构建Docker镜像
3. 停止并删除旧容器（如果存在）
4. 运行新容器并映射串口设备

#### 虚拟环境部署步骤：
1. 更新系统软件包
2. 安装必要的系统依赖
3. 安装串口硬件依赖
4. 创建应用目录
5. 克隆代码仓库
6. 清理旧的虚拟环境（如果存在）
7. 创建新的虚拟环境
8. 在虚拟环境中安装Python依赖
9. 创建系统服务文件
10. 启动服务并设置开机自启

### 5. 访问系统
部署完成后，可以通过以下地址访问系统：
- **系统地址**：http://localhost:5000
- **温振监控**：http://localhost:5000/vibration
- **光照监控**：http://localhost:5000/light
- **温湿度监控**：http://localhost:5000/temperature
- **系统概览**：http://localhost:5000/overview

## 默认配置

| 监控系统 | LoRa 目标地址 | 说明 |
|---------|-------------|------|
| 温振监控 | 0003 | 温度、振动、频率等监测 |
| 光照监控 | 5678 | 光照强度监测 |
| 温湿度监控 | 0002 | 温度和湿度监测 |

## 服务管理

### Docker容器管理

#### 查看容器状态
```bash
docker ps -a | grep lora-monitoring
```

#### 查看容器日志
```bash
docker logs lora-monitoring
```

#### 重启容器
```bash
docker restart lora-monitoring
```

#### 停止容器
```bash
docker stop lora-monitoring
```

#### 删除容器
```bash
docker rm lora-monitoring
```

#### 构建新镜像
```bash
docker build -t lora-monitoring:latest .
```

### 虚拟环境服务管理

#### 查看服务状态
```bash
sudo systemctl status lora-monitoring
```

#### 重启服务
```bash
sudo systemctl restart lora-monitoring
```

#### 停止服务
```bash
sudo systemctl stop lora-monitoring
```

#### 禁用服务
```bash
sudo systemctl disable lora-monitoring
```

## 虚拟环境管理

### 激活虚拟环境
```bash
cd /opt/lora-monitoring
source venv/bin/activate
```

### 安装额外依赖
```bash
cd /opt/lora-monitoring
source venv/bin/activate
pip install <package-name>
```

### 查看已安装依赖
```bash
cd /opt/lora-monitoring
source venv/bin/activate
pip list
```

## 日志查看

### Docker容器日志
```bash
docker logs lora-monitoring
```

### 虚拟环境服务日志
```bash
sudo journalctl -u lora-monitoring
```

## 故障排查

### 1. Docker部署问题

#### 容器无法启动
检查容器状态和日志：
```bash
docker ps -a | grep lora-monitoring
docker logs lora-monitoring
```

#### 串口设备映射问题
确保串口设备存在且权限正确：
```bash
ls -la /dev/ttyUSB*
ls -la /dev/ttyACM*
```

### 2. 虚拟环境部署问题

#### 服务无法启动
检查服务状态和日志：
```bash
sudo systemctl status lora-monitoring
sudo journalctl -u lora-monitoring
```

#### 串口无法打开
确保用户有串口访问权限：
```bash
sudo usermod -a -G dialout $USER
# 重新登录后生效
```

#### 依赖安装失败
尝试手动安装依赖：
```bash
cd /opt/lora-monitoring
# 使用虚拟环境中的pip
./venv/bin/pip install -r requirements.txt
```

#### 虚拟环境问题
如果虚拟环境损坏，可以重建：
```bash
cd /opt/lora-monitoring
# 删除旧的虚拟环境
rm -rf venv
# 创建新的虚拟环境
python3 -m venv venv
# 安装依赖
./venv/bin/pip install -r requirements.txt
# 重启服务
sudo systemctl restart lora-monitoring
```

## 技术支持
- **代码仓库**：https://github.com/mmitwang/lora-sysytem
- **部署文档**：本文件
- **系统要求**：Ubuntu 22.04 LTS
- **部署方式**：Docker容器部署（推荐）或虚拟环境部署，避免依赖冲突
