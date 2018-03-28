# -*- coding: utf-8 -*-

from discord.ext import commands
import discord
import ujson

class Guilds:
    def __init__(self, bot):
        self.bot = bot

    async def update_guild_count(self):
        await self.bot.change_presence(activity=discord.Activity(name=f'{config.prefixes[0]}help | {len(self.guilds)} guilds', type=discord.ActivityType.listening))
        payload = {'server_count': sum(1 for g in self.bot.guilds)}
        await self.bot.session.request('POST', f'https://ls.terminal.ink/api/v1/bots/{self.bot.user.id}', data=ujson.dumps(payload, ensure_ascii=True),
        headers={'Content-Type': 'application/json', 'Authorization': self.bot.config.dbl})
        await self.bot.session.request('POST', f'https://discordbots.org/api/bots/{self.bot.user.id}/stats', data=ujson.dumps(payload, ensure_ascii=True),
        headers={'Content-Type': 'application/json', 'Authorization': self.bot.config.terminal})
        await asyncio.sleep(1)

    async def on_ready(self):
        if self.bot.config.dbl or self.bot.config.terminal:
            await self.update_guild_count()
   
    async def on_guild_join(self, guild):
        if self.bot.config['dbl'] or self.bot.config.terminal:
            await self.update_guild_count()
    
    async def on_guild_remove(self, guild):
        if self.bot.config['dbl'] or self.bot.config.terminal:
            await self.update_guild_count()

def setup(bot):
    bot.add_cog(Guilds(bot))
