#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from discord.ext import commands
import discord
import config

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

bot.run(config.token)
