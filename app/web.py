"""Web路由模块"""

from flask import Blueprint, render_template
from app import app

# 创建Web蓝图
web_bp = Blueprint('web', __name__)


@web_bp.route('/')
def index():
    """主页面"""
    return render_template('overview.html', active_page='overview')


@web_bp.route('/overview')
def overview():
    """系统概览页面"""
    return render_template('overview.html', active_page='overview')


@web_bp.route('/temperature')
def temperature():
    """温湿度监控页面"""
    return render_template('temperature.html', active_page='temperature')


@web_bp.route('/vibration')
def vibration():
    """温振监控页面"""
    return render_template('vibration.html', active_page='vibration')


@web_bp.route('/video')
def video():
    """视频监控页面"""
    return render_template('video.html', active_page='video')


@web_bp.route('/light')
def light():
    """光照气体监控页面"""
    return render_template('light.html', active_page='light')


@web_bp.route('/config')
def config():
    """配置调试页面"""
    return render_template('index.html', active_page='config')
