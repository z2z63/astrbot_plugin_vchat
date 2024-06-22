import asyncio
import base64
import io
import logging
from pathlib import Path
from threading import Thread

import vchat.model as model
from nakuru import GuildMessage, GroupMessage, FriendMessage
from nakuru.entities.components import Plain, Image
from vchat import Core

from type.message import MessageMember, MessageType
from type.types import GlobalObject

logger = logging.getLogger('astrbot_plugin_vchat')
flag_not_support = False
try:
    from util.plugin_dev.api.v1.config import *
    from util.plugin_dev.api.v1.bot import (
        AstrMessageEvent,
        CommandResult,
    )
    from util.plugin_dev.api.v1.message import message_handler, AstrBotMessage
    from util.plugin_dev.api.v1.register import register_platform
    from model.platform._platfrom import Platform
    from util.plugin_dev.api.v1.config import load_config
except ImportError:
    flag_not_support = True
    print("导入接口失败。请升级到 AstrBot 最新版本。")


def my_handler():
    print("Hello, VChat!")


class VChatPlugin:
    def __init__(self, ctx: GlobalObject) -> None:
        put_config("VChat", "启用", "enable", False, "是否启用 VChat 插件")
        put_config("VChat", "管理员", "admin", "",
                   "输入`username`,多个管理员通过空格分隔，`username`通过/get_my_username获取")
        config = load_config("VChat")
        if config.get("enable", False):
            platform = WechatPlatform(my_handler)
            register_platform("wechat", platform, ctx)
            self.admin = [i for i in config.get("admin", "").split(" ") if i != ""]
            self.thread = Thread(target=self.vchat_run)
            self.thread.start()

    def run(self, ame: AstrMessageEvent):
        return CommandResult(
            hit=False,
            success=False,
            message_chain=[]
        )

    def info(self):
        return {
            "plugin_type": "platform",
            "name": "VChat",
            "desc": "通过VChat让AstrBot支持微信",
            "help": "输入 /keyword 查看关键词回复帮助。",
            "version": "v0.1",
            "author": "z2z63",
            "repo": "https://github.com/z2z63/VChat"
        }

    def vchat_run(self):
        asyncio.run(self.vchat_async_run())

    async def vchat_async_run(self):
        self.core = Core()
        await self.core.init()
        await self.core.auto_login(hot_reload=False, enable_cmd_qr=True)
        await self.core.send_msg("Hello, filehelper", to_username="filehelper")
        self.core.msg_register(
            msg_types=model.ContentTypes.TEXT, contact_type=model.ContactTypes.USER | model.ContactTypes.CHATROOM
        )(self.vchat_handle_message)
        await self.core.run()

    async def vchat_handle_message(self, msg: model.Message):
        if msg.from_.username == self.core.me.username:
            return  # 自己发的消息不处理
        assert isinstance(msg.content, model.TextContent)
        if msg.content.content.strip() == '/get_my_username':     # 平台类插件不支持添加命令
            await self.core.send_msg("你的username是：" + msg.from_.username, msg.from_.username)
            return

        amsg = AstrBotMessage()
        amsg.message = [Plain(msg.content.content)]
        amsg.sender = MessageMember(msg.from_.username, msg.from_.nickname)
        amsg.message_str = msg.content.content
        amsg.message_id = msg.message_id
        if msg.from_.username.startswith('@@'):
            amsg.type = MessageType.GROUP_MESSAGE
        elif msg.from_.username.startswith('@'):
            amsg.type = MessageType.FRIEND_MESSAGE

        session_id = msg.from_.username + "$$" + msg.to.username
        role = "admin" if msg.from_.username in self.admin else "member"
        result = await message_handler(
            message=amsg,
            platform="wechat",
            session_id=session_id,
            role=role,
        )
        if result is None:
            return
        if isinstance(result.result_message, str):
            await self.core.send_msg(result.result_message, msg.from_.username)
            return
        plain_text = ""
        for i in result.result_message:
            if isinstance(i, Plain):
                plain_text += i.text
            elif isinstance(i, Image):
                if i.path is not None:
                    image_path = i.path
                    await self.core.send_image(msg.from_.username, Path(image_path))
                else:
                    image_bytes = base64.b64decode(i.file[9:])
                    image = io.BytesIO(image_bytes)
                    await self.core.send_image(msg.from_.username, fd=image)

        if plain_text != "":
            await self.core.send_msg(plain_text, msg.from_.username)


class WechatPlatform(Platform):
    def __init__(self, message_handler: callable):
        super().__init__(message_handler)
        print(message_handler)

    async def reply_msg(self):
        print("reply_msg")

    async def handle_msg(self):
        print("handle_msg")

    async def send(self, target: Union[GuildMessage, GroupMessage, FriendMessage, str], message: Union[str, list]):
        print("send")

    async def send_msg(self, target: Union[GuildMessage, GroupMessage, FriendMessage, str], message: Union[str, list]):
        print("send_msg")
