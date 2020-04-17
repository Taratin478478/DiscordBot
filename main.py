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
from youtubeapi import YoutubeAPI
from data import db_session
from data.users import User
import youtube_dl

TOKEN = "NjkzMzYwNjMyOTQ2MzYwNDEx.XpoD_g.OwU7nAI-rlaAIwrCHcswcxjUo0A"
YT_KEY = 'AIzaSyAI-dchFZTy877OsHs8PJM_N3gY1abF8mY'
prefix = '!'
youtube = YoutubeAPI(YT_KEY)


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
            if command[0].lower() in ['lvl', 'level']:
                session = db_session.create_session()
                user = session.query(User).filter(User.name == str(message.author))[0]
                await message.channel.send(
                    f'Ваш уровень: {user.lvl}, {user.xp}/{(user.lvl + 1) * 100} xp')
                session.commit()
            elif command[0].lower() in ['leaderboard', 'top']:
                session = db_session.create_session()
                users = session.query(User).all()
                if len(users) > 10:
                    users = users[:10]
                m = ''
                for user in users:
                    m += f'{user.name[:-5]}: {user.lvl} lvl, {user.xp}/{(user.lvl + 1) * 100} xp\n'
                await message.channel.send(m)
            elif command[0].lower() == 'play':
                vc = message.author.voice
                if vc is None:
                    await message.channel.send('Вы не подключены к голосовому каналу')
                else:
                    result = youtube.search_videos(' '.join(command[1:]))[0]['id']['videoId']
                    with youtube_dl.YoutubeDL() as ydl:
                        song_info = ydl.extract_info(
                            "https://www.youtube.com/watch?v=" + result, download=False)
                    print(song_info)
                    vc = await vc.channel.connect()
                    vc.play(discord.FFmpegPCMAudio(song_info["formats"][0]["url"],
                                                   executable="D:/ffmpeg/bin/ffmpeg.exe"))
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
