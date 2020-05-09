import asyncio
import io
import os
from random import randint

import requests
import discord
import datetime
import sqlalchemy
import sqlalchemy.orm as orm
from imgurpython import ImgurClient
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec
from data import db_session
from data.users import User
import os
from yandex_music import Client, Chart, ChartItem

TOKEN = 'NjkzMzYwNjMyOTQ2MzYwNDEx.XrZcAA.2lmEV7PgL2epZ-7fFpsdZbVxrus'
YM_TOKEN = 'AgAAAAAqsmX2AAG8Xklspw80fEAAiPb8RY7-qIE'
prefix = '-'
ya_music = Client.from_token(YM_TOKEN)


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
        self.queue = asyncio.Queue()
        self.play_next_song = asyncio.Event()
        self.loop.create_task(self.audio_player_task())

    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
        for guild in self.guilds:
            print(
                f'{self.user} подключились к чату:\n'
                f'{guild.name}(id: {guild.id})')
            #            await guild.system_channel.send(
            #                f'{str(self.user)[:-5]} подключился и готов ко всему')
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

    async def audio_player_task(self):
        while True:
            self.play_next_song.clear()
            current = await self.queue.get()
            self.player = await self.vc.channel.connect()
            search_result = ya_music.search(text=current[0])
            self.track = search_result.best.result
            await current[1].send(
                'Включаю: ' + ', '.join([a.name for a in self.track.artists]) + ' - ' + self.track.title)
            info_list = ya_music.tracks_download_info(self.track.id)
            filtered_info_list = list(
                filter(lambda f: f.codec == "mp3",
                       sorted(info_list, key=lambda x: -x.bitrate_in_kbps)))
            download_info = filtered_info_list[0]
            url = download_info.get_direct_link()
            self.player.play(discord.FFmpegPCMAudio(url, executable="ffmpeg.exe"))
            await self.play_next_song.wait()
            await self.player.disconnect()

    async def on_message(self, message):
        if message.author == self.user:
            return
        elif message.content[0] == prefix:
            command = message.content[1:].split()
            if command[0].lower() in ['lvl', 'level']:
                session = db_session.create_session()
                user = session.query(User).filter(User.name == str(message.author))[0]
                await message.channel.send(
                    f'Ваш уровень: {user.lvl}, {user.xp}/{(user.lvl + 1) * 100} xp')
                session.commit()
            elif command[0].lower() in ['leaderboard', 'top']:
                session = db_session.create_session()
                users = session.query(User).all()
                m = ''
                users.sort(key=lambda u: (u.lvl, u.xp), reverse=True)
                m = ''
                if len(users) > 10:
                    users = users[:10]
                m = ''
                for user in users:
                    m += f'{user.name[:-5]}: {user.lvl} lvl, {user.xp}/{(user.lvl + 1) * 100} xp\n'
                await message.channel.send(m)
            elif command[0].lower() == 'play':
                self.vc = message.author.voice
                if self.vc is None:
                    await message.channel.send('Вы не подключены к голосовому каналу')
                else:
                    await message.channel.send(' '.join(command[1:]) + ' Добавлено в очередь')
                    await self.queue.put([command[1:], message.channel])
            elif command[0].lower() == 'chart':
                self.vc = message.author.voice
                if self.vc is None:
                    await message.channel.send('Вы не подключены к голосовому каналу')
                else:
                    await message.channel.send('включаю чарт Яндекс.Музыки')
                chart = ya_music.landing('chart')[0]
                for c in chart:
                    await self.queue.put([c.data.track.title, message.channel])
            elif command[0].lower() == 'song':
                await message.channel.send(self.track.title)
            elif command[0].lower() == 'stop':
                while not self.queue.empty():
                    self.queue.get_nowait()
                await self.player.disconnect()
            # -meme СКОРЕЕ ВСЕГО НЕ РАБОТАЕТ, ПОКА НЕ ПРОВЕРЯЛ
            elif command[0].lower() == 'meme':
                client_id = '5d6d51c3b6b7dc2'
                client_secret = '5a419654aae91de31d31a6697f3f07ff1d952748'
                client = ImgurClient(client_id, client_secret)
                embed = discord.Embed()
                embed.set_image(url=client.default_memes())
                await message.channel.send(embed=embed)
        session = db_session.create_session()
        user = session.query(User).filter(User.name == str(message.author))[0]
        user.xp += randint(7, 13)
        if user.xp >= (user.lvl + 1) * 100:
            user.lvl += 1
            user.xp = 0
        session.commit()


db_session.global_init("db/blogs.sqlite")
client = YLBotClient()
client.run(TOKEN)
