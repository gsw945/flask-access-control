# -*- coding: utf-8 -*-
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

from flask_debugtoolbar import DebugToolbarExtension
# [1] 引入相关方法和类
from auth.main import AUTH_NAME, record_auth_route, register_auth_menus, register_auth_routes, Base, sync_permissions
from auth.models import User, Role, Permission


app = Flask(__name__)
app.config['SECRET_KEY'] = '!secret!'
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SQLALCHEMY_ECHO'] = True

# [2]指定 model_class
db = SQLAlchemy(app, model_class=Base)
app.db = db

app.debug = True
toolbar = DebugToolbarExtension(app)

@app.route('/')
@record_auth_route('权限-访问首页')
def view_index():
    return render_template('index.html')

@app.route('/list')
def view_list():
    route_permissions = Permission.query.filter_by(category='route').all()
    menu_permissions = Permission.query.filter_by(category='menu').all()
    users = User.query.all()
    roles = Role.query.all()
    data = {
        'US': users,
        'RS': roles,
        'RPS': route_permissions,
        'MPS': menu_permissions
    }
    return render_template('list.html', **data)

# [3] 注册Auth路由
# [3.1] record_auth_route() 装饰器材-记录路由(视图函数)
# [3.2] register_auth_routes() 将视图函数转为endpoint，并添加到Auth
register_auth_routes(app)

# [4] 注册Auth菜单
# [4.1] 定义菜单
sidebar = [
    {
        'icon': 'fa fa-dashboard',
        'text': '概览',
        'type': 'url4',
        'value': AUTH_NAME + '.view_login'
    },
    {
        'icon': 'fa fa-file-text',
        'text': '测试',
        'type': 'group',
        'value': [
            {
                'icon': 'fa fa-circle-o',
                'text': '空白页',
                'type': 'url4',
                'value': AUTH_NAME + '.view_demo'
            },
            {
                'icon': 'fa fa-circle-o',
                'text': '玖亖伍',
                'type': 'href',
                'value': 'htts://blog.gsw945.com/'
            }
        ]
    },
    {
        'icon': 'fa fa-home',
        'text': '首页',
        'type': 'url4',
        'value': 'view_index'
    }
]
# [4.2] register_auth_routes() 函数-注册菜单
register_auth_menus(app, sidebar)

# 仅仅用于开发阶段和部署第一次启动初始化时
with app.test_request_context():
    # 创建数据库
    db.create_all()
    # [5] 同步数据库中的权限
    sync_permissions(app, db)


if __name__ == '__main__':
    app.run(debug=True, port=5005)