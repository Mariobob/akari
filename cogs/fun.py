# -*- coding: utf-8 -*-

from discord.ext import commands
import discord
import wolframalpha
from cleverwrap import CleverWrap
import random
import aiohttp
import asyncio
import functools

class Fun:
    """Fun stuff."""

    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config
        self.client = wolframalpha.Client(bot.config.app_id)
        self.invalid_strings = ["Nobody knows.",
                                "It's a mystery.",
                                "I have no idea.",
                                "No clue, sorry!",
                                "I'm afraid I can't let you do that.",
                                "Maybe another time.",
                                "Ask someone else.",
                                "That is anybody's guess.",
                                "Beats me.",
                                "I haven't the faintest idea."]
        self.cw = CleverWrap(bot.config.cwkey)
        
    async def get(self, url, head=None):
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=head) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                raise response.status

    @commands.command(aliases=['c', 'cbot'])
    async def clever(self, ctx, *, message):
        '''Say something to cleverbot.'''
        async with ctx.typing():
            await ctx.send(self.cw.say(message))

    @commands.command()
    async def cat(self, ctx):
        '''Get a random cat image.'''
        
        try:
            fact = await self.get(url='https://catfact.ninja/fact')
            e = discord.Embed(color=ctx.author.color, description=fact['fact'])
        except:
            self.bot.raven.CaptureException()
            await ctx.send('Something went wrong while getting your cat fact!')
        
        try:
            resp = await self.get(url='https://random.cat/meow')
            e.set_image(url=resp['file'])
        except:
            self.bot.raven.CaptureException()
            await ctx.send('Something went wrong while getting your cat image!')

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
    async def neko(self, ctx):
        '''Gets a random neko :3'''
        e = discord.Embed(color=ctx.author.color)
        resp = await self.get(url='https://nekos.life/api/neko')
        e.set_image(url=resp['neko'])
        e.set_footer(text='Powered by nekos.life')
        await ctx.send(embed=e)

    @commands.command()
    @commands.is_nsfw()
    async def lewdneko(self, ctx):
        '''Gets a random lewd neko o.o'''
        e = discord.Embed(color=ctx.author.color)
        resp = await self.get(url='https://nekos.life/api/lewd/neko')
        e.set_image(url=resp['neko'])
        e.set_footer(text='Powered by nekos.life')
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
                await ctx.send(f'```{types}```')
        else:
            await ctx.send(content=f'```{types}```')

    @commands.command()
    async def osu(self, ctx, *, user):
        try:
            respraw = await self.get(url=f'https://osu.ppy.sh/api/get_user?k={self.config.osu}&u={user}')
            resp = respraw[0]
        except Exception as e:
            await ctx.send(f'S-something went wrong!\n```py\n{e}```')
            return
        username     = resp.get('username', 'Error occured')
        userid       = resp.get('user_id', 'Error occured')
        try:
            acc = resp.get('accuracy', '0')
            accuracy = f'{round(float(acc))}%'
        except:
            accuracy = 'Not Available'
        timesplayed  = resp.get('playcount', 'Error occured')
        country      = resp.get('country', 'Error occured')
        pp           = resp.get('pp_rank', 'Error occured')
        level        = resp.get('level', 'Error occured')
        ranked_score = resp.get('ranked_score', 'Error occured')
        total_score  = resp.get('total_score', 'Error occured')
        stats        = {'Username': str(username), 
                        'ID': str(userid), 
                        'Accuracy':str(accuracy), 
                        'Times Played': str(timesplayed), 
                        'Country':str(country),
                        'PP':pp,
                        'Level':str(level),
                        'Ranked Score':str(ranked_score), 
                        'Total Score':str(total_score),
                        }
        e = discord.Embed(title=f'osu! stats for {username}', description='osu! stats\n', color=ctx.author.color)
        for stat in stats:
            e.add_field(name=stat, value=stats[stat])
        await ctx.send(embed=e)

        

    @commands.command()
    async def wolfram(self, ctx, *, query):
        """Query Wolfram Alpha."""
        def q(query):
            res = self.client.query(query)
            return res
        async def async_q(query):
            thing = functools.partial(q, query)
            return await self.bot.loop.run_in_executor(None, thing)
        res = await async_q(query)
        e = discord.Embed(title="Wolfram|Alpha", description="", color=ctx.author.color)
        def invalid():
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
