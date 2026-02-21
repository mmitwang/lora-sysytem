#!/bin/bash

# 一键部署脚本 - Ubuntu 22.04
# 适用于温振监控系统
# 使用虚拟环境避免依赖冲突

echo "====================================="
echo "温振监控系统一键部署脚本"
echo "Ubuntu 22.04 版本"
echo "使用虚拟环境部署"
echo "====================================="

# 检查是否为root用户
if [ "$(id -u)" != "0" ]; then
    echo "错误：请使用root用户运行此脚本"
    exit 1
fi

# 更新系统
echo "[1/9] 更新系统软件包..."
apt update && apt upgrade -y

# 安装必要的系统依赖
echo "[2/9] 安装必要的系统依赖..."
apt install -y python3 python3-pip python3-venv git build-essential libssl-dev libffi-dev python3-dev

# 安装串口硬件依赖
echo "[3/9] 安装串口硬件依赖..."
apt install -y python3-serial

# 创建应用目录
echo "[4/9] 创建应用目录..."
mkdir -p /opt/lora-monitoring
cd /opt/lora-monitoring

# 克隆代码仓库
echo "[5/9] 克隆代码仓库..."
git clone https://github.com/mmitwang/lora-sysytem.git .

# 清理旧的虚拟环境（如果存在）
echo "[6/9] 清理旧的虚拟环境..."
if [ -d "venv" ]; then
    rm -rf venv
fi

# 创建新的虚拟环境
echo "[7/9] 创建新的虚拟环境..."
python3 -m venv venv

# 激活虚拟环境并安装Python依赖
echo "[8/9] 安装Python依赖（仅在虚拟环境中）..."
# 使用完整路径执行pip，确保使用虚拟环境中的pip
/opt/lora-monitoring/venv/bin/pip install --upgrade pip
/opt/lora-monitoring/venv/bin/pip install -r requirements.txt

# 创建系统服务文件
echo "[9/9] 创建系统服务文件..."
cat > /etc/systemd/system/lora-monitoring.service << EOF
[Unit]
Description=LoRa Monitoring System
After=network.target

[Service]
User=root
WorkingDirectory=/opt/lora-monitoring
# 使用虚拟环境中的Python解释器
ExecStart=/opt/lora-monitoring/venv/bin/python app.py
# 确保环境变量正确
Environment="PATH=/opt/lora-monitoring/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 启动服务
echo "====================================="
echo "启动服务..."
systemctl daemon-reload
systemctl enable lora-monitoring
systemctl start lora-monitoring

# 检查服务状态
echo "====================================="
echo "检查服务状态..."
systemctl status lora-monitoring

# 显示部署结果
echo "====================================="
echo "部署完成！"
echo "====================================="
echo "服务已启动，访问地址：http://localhost:5000"
echo "默认配置："
echo "- 温振监控 LoRa 目标地址：0003"
echo "- 光照监控 LoRa 目标地址：5678"
echo "- 温湿度监控 LoRa 目标地址：0002"
echo ""
echo "部署特点："
echo "- 使用独立的Python虚拟环境"
echo "- 所有依赖仅安装在虚拟环境中"
echo "- 避免与系统其他Python依赖冲突"
echo "- 服务自动启动和重启"
echo "====================================="
