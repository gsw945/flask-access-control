# -*- coding: utf-8 -*-
import os
import builtins
from functools import wraps
from datetime import datetime
from collections import OrderedDict
import inspect

from flask import g, request, current_app, session
from flask.helpers import _endpoint_from_view_func


class Singleton(object):
    '''单例模式-基类'''
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            origin = super(Singleton, cls)
            cls._instance = origin.__new__(cls, *args, **kwargs)
        return cls._instance

class GlobalVar(Singleton, OrderedDict):
    """全局变量-类（兼容有序字典）"""
    pass

def is_callable(obj):
    '''判断对象是否是可调用对象（函数、方法等）'''
    if hasattr(builtins, 'callable'):
        return callable(obj)
    return hasattr(obj, '__call__')

def record_permission(permission, check_func=None, *check_args, **check_kwargs):
    '''
    路由绑定权限（可传入check_func自定义验证）

    permission 权限名
    check_func 权限核验函数
        请求来时执行，g.route_permission 可以取到权限名
        返回有效响应数据，则阻止视图函数执行
        返回None或空数据，才会调用视图函数
    check_args 权限核验函数所需参数
    check_kwargs 权限核验函数所需参数
    '''
    def decorator(view_func):
        nonlocal permission

        @wraps(view_func)
        def wrapped(*args, **kwargs):
            nonlocal permission, check_func, check_args, check_kwargs
            # 将权限添加到 上下文文变量g 中
            g.route_permission = permission
            # 打印当前请求的endpoint
            # print(request.endpoint)
            # 检查权限
            if is_callable(check_func):
                check_resp = check_func(*check_args, **check_kwargs)
                if bool(check_resp):
                    return check_resp
            ret = view_func(*args, **kwargs)
            return ret

        # 函数名
        func_name = wrapped.__name__
        # 函数所在模块
        module = inspect.getmodule(wrapped)
        # 模块文件
        module_filename = os.path.abspath(module.__file__)
        # 函数所在文件
        filename = inspect.getsourcefile(wrapped)
        filename = os.path.abspath(filename)
        # 获取行号（忽略源码）
        _source, lineno = inspect.getsourcelines(wrapped)
        # 以 (模块文件路径, 函数所在文件路径, 函数名, 函数在文件中定义行号) 作为键
        key = (module_filename, filename, func_name, lineno)
        # 全局变量
        GV = GlobalVar()
        # endpoint = _endpoint_from_view_func(wrapped)
        # 在蓝图中，未能获取到正确的endpoint
        # GV[key] = (endpoint, permission)
        # 以 权限名 作为值
        GV[key] = permission

        return wrapped

    return decorator