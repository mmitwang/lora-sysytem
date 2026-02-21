# 使用Ubuntu 22.04作为基础镜像
FROM ubuntu:22.04

# 设置工作目录
WORKDIR /app

# 更新系统并安装必要的依赖
RUN apt-get update && apt-get upgrade -y && \    apt-get install -y python3 python3-pip python3-dev build-essential git && \    apt-get clean && \    rm -rf /var/lib/apt/lists/*

# 克隆代码仓库
RUN git clone https://github.com/mmitwang/lora-sysytem.git .

# 安装Python依赖
RUN pip3 install --upgrade pip && \    pip3 install -r requirements.txt

# 复制环境变量配置文件
COPY .env .env

# 暴露端口
EXPOSE 5000

# 启动应用
CMD ["python3", "app.py"]