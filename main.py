import asyncio
import io
import requests
import discord
import datetime
import sqlalchemy
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec
from data import db_session
from data.users import User

TOKEN = "NjkzMzYwNjMyOTQ2MzYwNDEx.Xn79nQ.peYKjTtUz3EErirA10z_8fCNcgU"


def get_my_files(content):
    f = io.BytesIO(content)
    my_files = [
        discord.File(f, "tmpcat.jpg"),
    ]
    return my_files


class YLBotClient(discord.Client):
    def __init__(self):
        super().__init__()
        self.timers = []

    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
        for guild in self.guilds:
            print(
                f'{self.user} подключились к чату:\n'
                f'{guild.name}(id: {guild.id})')
            await guild.system_channel.send(
                f'{str(self.user)[:-5]} подключился и готов ко всему')
            session = db_session.create_session()
            members = [user.name for user in session.query(User).all()]
            for m in guild.members:
                if str(m) not in members:
                    user = User()
                    user.name = str(m)
                    session.add(user)
            session.commit()



    async def on_member_join(self, member):
        await member.create_dm()
        await member.dm_channel.send(
            f'Привет, {member.name}!'
        )

    async def on_message(self, message):
        if message.author == self.user:
            return
        else:
            session = db_session.create_session()
            print(str(message.author))
            user = session.query(User).filter(User.name == str(message.author))[0]
            print(user)
            user.xp += 10
            print(user.xp)
            session.commit()


db_session.global_init("db/blogs.sqlite")
client = YLBotClient()
client.run(TOKEN)
