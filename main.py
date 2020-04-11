import asyncio
import io
from random import randint

import requests
import discord
import datetime
import sqlalchemy
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec
from data import db_session
from data.users import User

TOKEN = "NjkzMzYwNjMyOTQ2MzYwNDEx.XpG_mw.8dtO7uDgdZiHHP9UYEnyAHsA64o"
prefix = '!'

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
        elif message.content[0] == prefix:
            command = message.content[1:].split()
            print(prefix, command)
            if command[0].lower() == 'rank':
                session = db_session.create_session()
                user = session.query(User).filter(User.name == str(message.author))[0]
                await message.channel.send(f'Ваш уровень: {user.lvl}, {user.xp}/{(user.lvl + 1) * 100} xp')
                session.commit()
            elif command[0].lower() == 'leaderboard':
                session = db_session.create_session()
                users = session.query(User).all()
                if len(users) > 10:
                    users = users[:10]
                m = ''
                for user in users:
                    m += f'{user.name[:-5]}: {user.lvl} lvl, {user.xp}/{(user.lvl + 1) * 100} xp\n'
                await message.channel.send(m)
        else:
            session = db_session.create_session()
            user = session.query(User).filter(User.name == str(message.author))[0]
            print(str(message.author), user.xp)
            user.xp += randint(7, 13)
            if user.xp >= (user.lvl + 1) * 100:
                user.lvl += 1
                user.xp = 0
            session.commit()


db_session.global_init("db/blogs.sqlite")
client = YLBotClient()
client.run(TOKEN)
