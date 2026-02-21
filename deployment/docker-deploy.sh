#!/bin/bash

# Docker一键部署脚本 - Ubuntu 22.04
# 适用于温振监控系统

echo "====================================="
echo "温振监控系统Docker一键部署脚本"
echo "Ubuntu 22.04 版本"
echo "使用Docker容器部署"
echo "====================================="

# 检查是否为root用户
if [ "$(id -u)" != "0" ]; then
    echo "错误：请使用root用户运行此脚本"
    exit 1
fi

# 检查并安装Docker
if ! command -v docker &> /dev/null; then
    echo "[1/4] 安装Docker..."
    apt update && apt install -y docker.io
    systemctl enable docker
    systemctl start docker
else
    echo "[1/4] Docker已安装"
fi

# 进入部署目录
cd "$(dirname "$0")"

# 构建Docker镜像
echo "[2/4] 构建Docker镜像..."
docker build -t lora-monitoring:latest .

# 停止并删除旧容器（如果存在）
if [ "$(docker ps -aq -f name=lora-monitoring)" ]; then
    echo "[3/4] 停止并删除旧容器..."
    docker stop lora-monitoring
    docker rm lora-monitoring
fi

# 运行新容器
echo "[4/4] 运行Docker容器..."
docker run -d \
    --name lora-monitoring \
    --restart unless-stopped \
    -p 5000:5000 \
    --device=/dev/ttyUSB0:/dev/ttyUSB0 \
    --device=/dev/ttyACM0:/dev/ttyACM0 \
    lora-monitoring:latest

# 检查容器状态
echo "====================================="
echo "检查容器状态..."
docker ps -a | grep lora-monitoring

# 显示部署结果
echo "====================================="
echo "Docker部署完成！"
echo "====================================="
echo "服务已启动，访问地址：http://localhost:5000"
echo "默认配置："
echo "- 温振监控 LoRa 目标地址：0003"
echo "- 光照监控 LoRa 目标地址：5678"
echo "- 温湿度监控 LoRa 目标地址：0002"
echo ""
echo "部署特点："
echo "- 使用Docker容器隔离运行环境"
echo "- 避免与系统其他依赖冲突"
echo "- 容器自动重启"
echo "- 串口设备映射到容器内"
echo "====================================="
echo "Docker容器管理命令："
echo "- 查看容器状态：docker ps -a | grep lora-monitoring"
echo "- 查看容器日志：docker logs lora-monitoring"
echo "- 重启容器：docker restart lora-monitoring"
echo "- 停止容器：docker stop lora-monitoring"
echo "- 删除容器：docker rm lora-monitoring"
echo "- 构建新镜像：docker build -t lora-monitoring:latest ."
echo "====================================="