# -*- coding: utf-8 -*-
import os
import inspect

from .models import Base, User, Role, Permission, role_permission_map
from .apis import auth_app, record_permission
from .decorators import GlobalVar


def bind_app(app, url_prefix=None):
    '''
    将auth添加到Flask应用
    注意：一定需要在所有路由都注册了之后再调用
    '''
    # 注册蓝图( url_prefix 默认为 '/auth')
    app.register_blueprint(auth_app, url_prefix=url_prefix)

    app.route_map = {}
    GV = GlobalVar()
    for endpoint in app.view_functions:
        view_func = app.view_functions[endpoint]
        func_name = view_func.__name__
        module = inspect.getmodule(view_func)
        module_filename = os.path.abspath(module.__file__)
        filename = inspect.getsourcefile(view_func)
        filename = os.path.abspath(filename)
        _source, lineno = inspect.getsourcelines(view_func)
        key = (module_filename, filename, func_name, lineno)
        if key in GV:
            permission = GV[key]
            app.route_map[endpoint] = permission
    GV.clear()
    del GV

def sync_permissions(app, db):
    '''
    权限同步，以程序中收集的endpoint为准，更新数据库中的记录
    '''
    # 3 种情形
    #     1. code中没有, db中有, delete
    #     2. code中有, db中有, update
    #     3. code中有, db中没有, insert
    '''
    # debug
    print(app.route_map)
    for endpoint in app.route_map:
        permission = app.route_map[endpoint]
        print(endpoint, '->', permission)
    '''
    # 挂载点列表
    endpoint_list = list(app.route_map.keys())
    # 情形-1
    # 代码中不存在，但数据库中有的挂载点
    ni_permissions = Permission.query.filter(
        Permission.endpoint.notin_(endpoint_list)
    ).all()
    # 权限ID
    ni_pids = list(map(lambda p: p.pid, ni_permissions))
    # 删除角色-权限关联
    tb_rp = role_permission_map
    stmt = tb_rp.delete().where(
        tb_rp.columns.permission_id.in_(ni_pids)
    )
    # 执行删除 角色-权限关联 操作
    del_rowcount = db.session.execute(stmt).rowcount
    # print(del_rowcount)
    # 执行删除 权限 操作
    for ni_p in ni_permissions:
        db.session.delete(ni_p)
    db.session.commit()
    
    # 情形-2
    # 代码中存在，数据库中也有的挂载点
    in_permissions = Permission.query.filter(
        Permission.endpoint.in_(endpoint_list)
    ).all()
    for p_obj in in_permissions:
        # 比对权限名，如果不同，则更新
        new_name = app.route_map[p_obj.endpoint]
        if p_obj.name != new_name:
            p_obj.name = new_name
        # 移除已经处理了的挂载点
        endpoint_list.remove(p_obj.endpoint)
    db.session.commit()
    # 情形-3
    # 新加入的权限，保存到数据库
    new_permissions = list(map(
        lambda endpoint: Permission(endpoint, app.route_map[endpoint]),
        endpoint_list
    ))
    db.session.add_all(new_permissions)
    db.session.commit()