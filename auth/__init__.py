# -*- coding: utf-8 -*-
from flask import Blueprint
# from flask_sqlalchemy import SQLAlchemy


# 实际使用中，db从外部导入
# db = SQLAlchemy()
auth_app = Blueprint(
    'auth',
    __name__,
    url_prefix='/auth'
)