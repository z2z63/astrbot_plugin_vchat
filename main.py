import base64
import io
from pathlib import Path
from typing import Any, List

from nakuru.entities.components import BaseMessageComponent, Plain, Image

from type.astrbot_message import AstrBotMessage, MessageMember, MessageType

flag_not_support = False

from vchat import Core
import vchat.model as model

try:
    from util.plugin_dev.api.v1.bot import Context, AstrMessageEvent, CommandResult
    from util.plugin_dev.api.v1.config import load_config, put_config
    from util.plugin_dev.api.v1.platform import Platform
    from util.plugin_dev.api.v1.message import MessageHandler
    from util.plugin_dev.api.v1.register import register_platform
except ImportError:
    flag_not_support = True
    print("导入接口失败。请升级到 AstrBot 最新版本。")


class WechatPlatform(Platform):
    def __init__(self, context: Context, config: dict[str, bool]):
        super().__init__()
        self.core = Core()
        self.config = config
        self.context = context
        context.register_task(self.run(), "vchat-core-run")

    async def run(self):
        await self.core.init()
        enable_cmd_qr = self.config.get("enable_cmd_qr", False)
        hot_reload = self.config.get("hot_reload", True)
        await self.core.auto_login(hot_reload=hot_reload, enable_cmd_qr=enable_cmd_qr)
        await self.core.send_msg("Hello, filehelper", to_username="filehelper")

        @self.core.msg_register(msg_types=model.ContentTypes.TEXT,
                                contact_type=model.ContactTypes.USER | model.ContactTypes.CHATROOM)
        async def _(msg: model.Message):
            await self.handle_msg(self.convert_message(msg))

        await self.core.run()

    @staticmethod
    def convert_message(msg: model.Message) -> AstrBotMessage:
        assert isinstance(msg.content, model.TextContent)
        amsg = AstrBotMessage()
        amsg.message = [Plain(msg.content.content)]
        sender = msg.chatroom_sender or msg.from_
        amsg.sender = MessageMember(sender.username, sender.nickname)
        amsg.message_str = msg.content.content
        amsg.message_id = msg.message_id
        if isinstance(msg.from_, model.User):
            amsg.type = MessageType.FRIEND_MESSAGE
        elif isinstance(msg.from_, model.Chatroom):
            amsg.type = MessageType.GROUP_MESSAGE
        else:
            assert False, '不处理公众号'
        amsg.raw_message = msg
        session_id = msg.from_.username + "$$" + msg.to.username
        if msg.chatroom_sender is not None:
            session_id += '$$' + msg.chatroom_sender.username
        amsg.session_id = session_id
        return amsg

    async def reply_msg(self, message: AstrBotMessage, result_message: List[BaseMessageComponent]):
        assert isinstance(message.raw_message, model.Message)
        username = message.raw_message.from_.username
        # username = message.sender.user_id
        if isinstance(result_message, str):
            result_message = [Plain(result_message)]
        await self._send_message(username, result_message)

    async def send_msg(self, target: Any, result_message: CommandResult):
        raise NotImplementedError

    async def _send_message(self, username: str, result_message: List[BaseMessageComponent]):
        plain_text = ""
        for i in result_message:
            if isinstance(i, Plain):
                plain_text += i.text
            elif isinstance(i, Image):
                if i.path is not None:
                    image_path = i.path
                    await self.core.send_image(username, Path(image_path))
                else:
                    image_bytes = base64.b64decode(i.file[9:])
                    image = io.BytesIO(image_bytes)
                    await self.core.send_image(username, fd=image)

        if plain_text != "":
            await self.core.send_msg(plain_text, username)

    async def handle_msg(self, message: AstrBotMessage):
        # role = "admin" if message.sender.user_id in self.admin else "member"
        role = "member"
        ame = AstrMessageEvent.from_astrbot_message(message, self.context, "wechat", message.session_id, role)
        message_result = await self.context.message_handler.handle(ame)
        if not message_result:
            return
        await self.reply_msg(message, message_result.result_message)


class Main:
    """
    AstrBot 会传递 context 给插件。

    - context.register_commands: 注册指令
    - context.register_task: 注册任务
    - context.message_handler: 消息处理器(平台类插件用)
    """

    def __init__(self, context: Context) -> None:
        self.context = context
        put_config("VChat", "使用vchat插件", "enable", False, "打开此开关以启用vchat插件")
        put_config("VChat", "在终端打印二维码", "enable_cmd_qr", False,
                   "如果在docker容器或服务器等无桌面环境下运行，请打开此开关")
        put_config("VChat", "启用热重载", "hot_reload", True, "热重载允许几小时内无需扫码直接登录")

        config = load_config("VChat")
        if config.get("enable", False):
            self.platform = WechatPlatform(context, config)
            register_platform('wechat', context, self.platform)
