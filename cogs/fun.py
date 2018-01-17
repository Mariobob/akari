# -*- coding: utf-8 -*-

from discord.ext import commands
import discord
import wolframalpha
import random
from aiohttp import ClientSession
import asyncio

class Fun:
    """Fun stuff."""

    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config
        self.client = wolframalpha.Client(bot.config.app_id)
        self.invalid_strings = ["Nobody knows.", "It's a mystery.", "I have no idea.", "No clue, sorry!", "I'm afraid I can't let you do that.", "Maybe another time.", "Ask someone else.", "That is anybody's guess.", "Beats me.", "I haven't the faintest idea."]
        
    async def get(self, url, head=None):
        async with ClientSession() as session:
            async with session.get(url, headers=head) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                return response.status

    @commands.command()
    async def cat(self, ctx):
        '''Get a random cat image.'''
        e = discord.Embed(color=ctx.author.color)
        resp = await self.get(url='https://random.cat/meow')
        e.set_image(url=resp['file'])
        e.set_footer(text='Powered by random.cat')
        await ctx.send(embed=e)

    @commands.command()
    async def dog(self, ctx):
        '''Get a random dog image.'''
        e = discord.Embed(color=ctx.author.color)
        resp = await self.get(url='https://random.dog/woof.json')
        e.set_image(url=resp['url'])
        e.set_footer(text='Powered by random.dog')
        await ctx.send(embed=e)

    @commands.command()
    async def weeb(self, ctx, type=None):
        '''Fetch a type from weeb.sh. Call without args to get a list of types.'''
        head = {'Authorization': f'Bearer {self.config.weebsh}'}
        types = self.config.weebtypes['types']
        if type:
            if type in types:
                e = discord.Embed(color=ctx.author.color)
                resp = await self.get(url=f'https://api.weeb.sh/images/random?type={type}', head=head)
                e.set_image(url=resp['url'])
                e.set_footer(text='Powered by weeb.sh')
                await ctx.send(embed=e)
            else:
                await ctx.send('oof')
                await ctx.send(f'```{types}```')
        else:
            await ctx.send(content=f'```{types}```')

    @commands.command()
    async def osu(self, ctx, user):
        resp = await self.get(url=f'https://osu.ppy.sh/api/get_user?k={self.config.osu}&u={user}')[0]
        username = resp['username']
        userid = resp['user_id']
        accuracy = str(round(int(resp['accuracy']))) + '%'
        timesplayed = resp['playcount']
        country = resp['country']
        pp = resp['pp_ranked']
        level = resp['level']
        ranked_score = resp['ranked_score']
        total_score = resp['total_score']
        await ctx.send(resp)

    @commands.command()
    async def wolfram(self, ctx, *, query):
        """Query Wolfram Alpha."""
        res = self.client.query(query)
        e = discord.Embed(title="Wolfram|Alpha", description="", color=ctx.author.color)
        def invalid():
            """Invalidates a query"""
            e.add_field(name="Query", value=query, inline=False)
            e.add_field(name="Result", value=random.choice(self.invalid_strings)+"`(Invalid or undefined query)`", inline=False)
        try:
            r = next(res.results).text
            if r == "(undefined)" or r == "(data not available)":
                invalid()
            else:
                e.add_field(name="Query", value=query, inline=False)
                e.add_field(name="Result", value=r, inline=False)
        except:
            invalid()
        await ctx.send(embed=e)

def setup(bot):
    bot.add_cog(Fun(bot))
