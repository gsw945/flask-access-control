# -*- coding: utf-8 -*-
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from flask_debugtoolbar import DebugToolbarExtension
from auth.main import record_permission, bind_app, Base, sync_permissions

app = Flask(__name__)
app.config['SECRET_KEY'] = '!secret!'
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app, model_class=Base)
app.db = db

app.debug = True
toolbar = DebugToolbarExtension(app)

@app.route('/')
@record_permission('权限-访问首页')
def view_index():
    return '<bdoy></body>'

# 绑定auth
bind_app(app)

# 仅仅用于开发阶段和部署第一次启动初始化时
with app.test_request_context():
    # 创建数据库
    db.create_all()
    # 同步数据库中的权限
    sync_permissions(app, db)


if __name__ == '__main__':
    app.run(debug=True, port=5005)