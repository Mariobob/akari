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


    @commands.command()
    async def osu(self, ctx, user):
        async with ClientSession() as session:
            async with session.get(f'https://osu.ppy.sh/api/get_user?k={self.config.osu}&u={user}') as response:
                response = await response.json
        await ctx.send(response)

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
