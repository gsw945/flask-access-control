# flask-access-control
Flask访问控制(封装了RBAC模型、蓝图和装饰器)

### 运行
```
pip install -r requirements.txt
python demo.py
```

### 业务知识
> #### 访问控制(access contrl)
> * **认证(authentication)**: 你是谁(who you are), 身份验证。
> * **授权(authorization)**: 你可以做什么(what can you do), 权限验证。
> 
> #### RBAC
> > 基于角色的访问控制(Role-Based policies Access Control)
> * **用户(User)**
> * **角色(Role)**
> * **资源(Resource)**
> * 用户-角色 关联(User-Role-Map)：用户所分配的角色(一个用户，可以分配多个角色), **用户分组**
> * 角色-资源 关联(Role-Resource-Map)：某个角色下的用户，可以操作哪些资源, **操作权限**
> 
> #### 延伸阅读
> * https://www.cnblogs.com/zkwarrior/p/5792947.html
> * https://www.cnblogs.com/rongfengliang/p/3982011.html
> * http://www.cnblogs.com/shijiaqi1066/p/3793894.html
> * https://segmentfault.com/q/1010000004280905