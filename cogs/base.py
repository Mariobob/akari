import io
import traceback
import sys
import textwrap
from contextlib import redirect_stdout
from discord.ext import commands
import discord

class Base:
    """Basic stuff."""

    def __init__(self, bot):
        self.bot = bot
        self._last_result = None

    # Stats

    @commands.command(aliases=['latency', 'pong'])
    async def ping(self, ctx):
        await ctx.send(f'p-pong! ({round(self.bot.latency*1000)}ms)')

    @commands.command(aliases=['about'])
    async def info(self, ctx):
        e = discord.Embed(title="Akari", color=ctx.author.color, url="https://akaribot.tk")

    # Owner Stuff

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    @commands.command(name='echo', hidden=True)
    @commands.is_owner()
    async def owner_echo(self, ctx, content):
        await ctx.send(content)

    @commands.command(name='load', hidden=True)
    @commands.is_owner()
    async def cog_load(self, ctx, *, module):
        """Loads a module."""
        try:
            self.bot.load_extension(module)
        except Exception as e:
            await ctx.send(f'S-sorry, senpai... b-but:```py\n{traceback.format_exc()}\n```')
        else:
            await ctx.send('O-ok, I have loaded! desu~')

    @commands.command(name='unload', hidden=True)
    @commands.is_owner()
    async def cog_unload(self, ctx, *, module):
        """Unloads a module."""
        try:
            self.bot.unload_extension(module)
        except Exception as e:
            await ctx.send(f'S-sorry, senpai... b-but:```py\n{traceback.format_exc()}\n```')
        else:
            await ctx.send('O-ok, I have unloaded! desu~')

    @commands.command(name='reload', hidden=True)
    @commands.is_owner()
    async def cog_reload(self, ctx, *, module):
        """Reloads a module."""
        try:
            self.bot.unload_extension(module)
            self.bot.load_extension(module)
        except Exception as e:
            await ctx.send(f'S-sorry, senpai... b-but:```py\n{traceback.format_exc()}\n```')
        else:
            await ctx.send('O-ok, I have r-reloaded! desu~')
    
    @commands.command(pass_context=True, hidden=True, name='eval')
    @commands.is_owner()
    async def _eval(self, ctx, *, body: str):
        """Evaluates a code"""

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except:
                pass

            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')

def setup(bot):
    bot.add_cog(Base(bot))