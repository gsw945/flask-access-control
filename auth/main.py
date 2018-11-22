# -*- coding: utf-8 -*-
import os
import inspect

from flask import g, request, current_app, session

from .models import Base, User, Role, Permission, role_permission_map
from .apis import auth_app
from .helper import record_auth_route, RouteCollection


AUTH_NAME = auth_app.name

def register_auth_routes(app, url_prefix=None):
    '''
    将auth添加到Flask应用
    注意：一定需要在所有路由都注册了之后再调用
    '''
    # 注册蓝图( url_prefix 默认为 '/auth')
    app.register_blueprint(auth_app, url_prefix=url_prefix)

    app.auth_route_map = {}
    RC = RouteCollection()
    for endpoint in app.view_functions:
        view_func = app.view_functions[endpoint]
        func_name = view_func.__name__
        module = inspect.getmodule(view_func)
        module_filename = os.path.abspath(module.__file__)
        filename = inspect.getsourcefile(view_func)
        filename = os.path.abspath(filename)
        _source, lineno = inspect.getsourcelines(view_func)
        key = (module_filename, filename, func_name, lineno)
        if key in RC:
            permission = RC[key]
            app.auth_route_map[endpoint] = permission
    RC.clear()
    del RC

def register_auth_menus(app, menus):
    '''菜单注册'''
    allowed_types = ['link', 'url4']
    app.auth_menu_map = {}
    for item in menus:
        if item['type'] == 'group':
            for sub_item in item['value']:
                app.auth_menu_map[sub_item['value']] = sub_item['text']
        else:
            if item['type'] in allowed_types:
                app.auth_menu_map[item['value']] = item['text']

def sync_permissions(app, db):
    '''
    权限同步，以程序中收集的(category, record)为准，更新数据库中的记录
    '''
    # 3 种情形
    #     1. code中没有, db中有, delete
    #     2. code中有, db中有, update
    #     3. code中有, db中没有, insert
    '''
    # debug
    print(app.auth_route_map)
    for record in app.auth_route_map:
        permission_text = app.auth_route_map[record]
        print(('route', record), '->', permission_text)
    print(app.auth_menu_map)
    for record in app.auth_menu_map:
        permission_text = app.auth_menu_map[record]
        print(('route', record), '->', permission_text)
    '''
    # 记录列表(route 和 menu)
    route_list = list(app.auth_route_map.keys())
    menu_list = list(app.auth_menu_map.keys())
    # 情形-1
    # 代码中不存在，但数据库中有的记录
    ni_routes = Permission.query.filter(
        Permission.record.notin_(route_list) &
        (Permission.category == 'route')

    ).all()
    ni_menus = Permission.query.filter(
        Permission.record.notin_(menu_list) &
        (Permission.category == 'menu')

    ).all()
    # 权限ID
    ni_pids = list(map(lambda p: p.pid, ni_routes + ni_menus))
    # 删除角色-权限关联
    tb_rp = role_permission_map
    stmt = tb_rp.delete().where(
        tb_rp.columns.permission_id.in_(ni_pids)
    )
    # 执行删除 角色-权限关联 操作
    del_rowcount = db.session.execute(stmt).rowcount
    # print(del_rowcount)
    # 执行删除 权限 操作
    for ni_p in ni_routes:
        db.session.delete(ni_p)
    for ni_p in ni_menus:
        db.session.delete(ni_p)
    db.session.commit()
    
    # 情形-2
    # 代码中存在，数据库中也有的记录
    in_routes = Permission.query.filter(
        Permission.record.in_(route_list) &
        (Permission.category == 'route')

    ).all()
    in_menus = Permission.query.filter(
        Permission.record.in_(menu_list) &
        (Permission.category == 'menu')

    ).all()
    for p_obj in in_routes:
        # 比对权限名，如果不同，则更新
        new_name = app.auth_route_map[p_obj.record]
        if p_obj.name != new_name:
            p_obj.name = new_name
        # 移除已经处理了的记录
        route_list.remove(p_obj.record)
    for p_obj in in_menus:
        # 比对权限名，如果不同，则更新
        new_name = app.auth_menu_map[p_obj.record]
        if p_obj.name != new_name:
            p_obj.name = new_name
        # 移除已经处理了的记录
        menu_list.remove(p_obj.record)
    db.session.commit()
    # 情形-3
    # 新加入的权限，保存到数据库
    new_routes = list(map(
        lambda ri: Permission(app.auth_route_map[ri], ri, 'route'),
        route_list
    ))
    db.session.add_all(new_routes)
    new_menus = list(map(
        lambda mi: Permission(app.auth_menu_map[mi], mi, 'menu'),
        menu_list
    ))
    db.session.add_all(new_menus)
    db.session.commit()