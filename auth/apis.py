# -*- coding: utf-8 -*-
from flask import jsonify, g, request

from . import auth_app
from .models import Permission
from .decorators import record_permission


@auth_app.route('/login')
@record_permission('权限-登录')
def view_login():
    return jsonify({})

def ac_check():
    print('访问[{0}], 需要[{1}]权限'.format(request.endpoint, g.route_permission))
    obj = Permission.query.filter_by(name=g.route_permission).first()
    return jsonify({
        'error': 0,
        'desc': 'just a demo',
        'data': {
            'debug': '访问验证, 已阻止视图函数执行',
            'TODO': '读取用户身份信息（角色），判断权限',
            'code': {
                'permission': g.route_permission,
                'endpoint': request.endpoint
            },
            'db': obj.to_dict() if isinstance(obj, Permission) else None
        }
    })

@auth_app.route('/demo')
@record_permission('权限-Demo', check_func=ac_check)
def view_demo():
    return jsonify({})