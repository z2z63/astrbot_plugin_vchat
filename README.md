# VChat provides wechat platform support for AstrBot
VChat插件为AstrBot提供了微信平台支持
# VChat
本插件使用 [VChat](https://github.com/z2z63/VChat) 接入微信，使用 UOS 微信 API ，相比网页版微信解除了以下限制
- 不需要在2017年之前登录过微信网页端
- 不需要开通支付功能
- 新注册的微信号也能使用

# 如何使用
1. 新注册一个微信号
2. 安装VChat插件
3. 在AstrBot仪表盘中启用VChat插件
4. enjoy

## 如何设置管理员
给机器人发送`/get_my_username`，获取自己的`username`，添加到仪表盘中VChat插件配置即可，多个管理员用空格分隔  
> **Note:** 由于UOS微信API的限制，只能获取用户的`username`，相当于**临时**ID，每次重新登录其值都会改变，需要重新设置管理员。
> 目前并没有能在两次登录之间唯一标识一个联系人的方法


# 反馈
请使用github issue  
欢迎PR

# 重要
使用本项目默认用户已经阅读并知悉[微信个人账号使用规范](https://weixin.qq.com/cgi-bin/readtemplate?&t=page/agreement/personal_account&lang=zh_CN)

推荐单独注册一个微信号，并严格限制其用途，严格遵守《计算机软件保护条例》（2013修订）第十七条规定，禁止商用
> 为了学习和研究软件内含的设计思想和原理，通过安装、显示、传输或者存储软件等方式使用软件的，可以不经软件著作权人许可

一切由于使用本项目造成的后果由使用者自行承担

如有侵权，请联系作者删除
