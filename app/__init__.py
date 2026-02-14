"""物联网监控系统应用包"""

import os
from flask import Flask
from flask_cors import CORS

from app.config import Config
from app.database import init_db

# 创建Flask应用实例
# 指定模板目录为项目根目录下的templates
app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates'))
app.config.from_object(Config)

# 启用CORS
CORS(app)

# 初始化数据库
init_db()

# 导入路由
from app import api, web
