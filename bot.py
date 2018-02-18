#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from discord.ext import commands
import discord
import config
import aiohttp
import asyncio

class Bot(commands.AutoShardedBot):
    def __init__(self, **kwargs):
        self.config = config
        super().__init__(command_prefix=commands.when_mentioned_or('=>'), **kwargs)
        for cog in config.cogs:
            try:
                self.load_extension(cog)
            except Exception as e:
                print('Could not load extension {0} due to {1.__class__.__name__}: {1}'.format(cog, e))

    async def on_ready(self):
        print('Logged on as {0} (ID: {0.id})'.format(self.user))
        await bot.change_presence(game=discord.Game(name="=>help | Akarin!"))

bot = Bot()

with open('blacklist.txt') as f:
    bot.config.blacklist = f.readlines()
    bot.config.blacklist = [f.strip() for f in bot.config.blacklist] 

async def update_types():
    await bot.wait_until_ready()
    while not bot.is_closed():
        async with aiohttp.ClientSession() as session:
            head = {'Authorization': f'Bearer {bot.config.weebsh}'}
            async with session.get(url='https://api.weeb.sh/images/types', headers=head) as response:
                bot.config.weebtypes = await response.json()
            await asyncio.sleep(1800) # sleeps every 30 minutes

async def server_count():
    await bot.wait_until_ready()
    while not bot.is_closed():
        async with aiohttp.ClientSession() as session:
            payload = {'server_count': len(bot.guilds)}
            header_one = {'Content-Type': 'application/json', 'Authorization': bot.config.terminal}
            header_two = {'Content-Type': 'application/json', 'Authorization': bot.config.dbl}
            # Terminal.Ink
            await session.post(f'https://ls.terminal.ink/api/v1/bots/{bot.user.id}', json=payload, headers=header_one)
            # Discord Bot List
            await session.post(f'https://discordbots.org/api/bots/{bot.user.id}/stats', json=payload, headers=header_two)
            await asyncio.sleep(1800) # sleeps every 30 minutes


bot.loop.create_task(server_count()) # creates background task

bot.loop.create_task(update_types())
bot.run(config.token)
