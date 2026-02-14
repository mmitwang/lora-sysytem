"""物联网监控系统主应用文件"""

from app import app
from app.api import api_bp
from app.web import web_bp

# 注册蓝图
app.register_blueprint(api_bp)
app.register_blueprint(web_bp)

if __name__ == '__main__':
    """运行应用"""
    app.run(debug=True, host='0.0.0.0', port=5000)
