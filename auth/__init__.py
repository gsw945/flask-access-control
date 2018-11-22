# -*- coding: utf-8 -*-
from flask import Blueprint
# from flask_sqlalchemy import SQLAlchemy


# 实际使用中，db从外部导入
# db = SQLAlchemy()
NAME = 'auth'
auth_app = Blueprint(
    NAME,
    __name__,
    url_prefix='/auth'
)
setattr(auth_app, 'name', NAME)