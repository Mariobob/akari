# -*- coding: utf-8 -*-

import traceback
import sys
from discord.ext import commands
import discord

class Checks:
    """Some checks, like blacklist."""

    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config
        bot.add_check(self.blacklisted)

    async def blacklisted(self, ctx):
        if str(ctx.author.id) in self.config.blacklist:
            await ctx.send('Blacklisted from bot, what did you do? :C')
            return False
        return True

    async def save_blacklist(self, blacklist):
        with open('blacklist.txt', 'w') as f:
            f.write('\n'.join(blacklist))
            self.config.blacklist = blacklist

    @commands.group()
    @commands.is_owner()
    async def blacklist(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(f'Blacklist: ```py\n{self.bot.config.blacklist}```')
    
    @blacklist.command()
    async def add(self, ctx, user: discord.User):
        blacklist = self.config.blacklist
        if str(user.id) in blacklist:
            await ctx.send(f'{user.name} already in blacklist')
        else:
            blacklist.append(str(user.id))
            await self.save_blacklist(blacklist)
            await ctx.send(f'Added {user.name} to blacklist')

    @blacklist.command()
    async def remove(self, ctx, user: discord.User):
        blacklist = self.config.blacklist
        try:
            blacklist.remove(str(user.id))
            await ctx.send(f'Removed {user.name} from blacklist')
        except:
            await ctx.send(f'{user.name} not in blacklist!')
        
        await self.save_blacklist(blacklist)

    async def on_guild_join(self, guild):
        if guild.id == 417837451994988554:
            return
        bots = sum(m.bot for m in guild.members)
        users = guild.member_count - bots
        
        if bots > round(3*users/4):
            await guild.leave()

    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command.
        ctx   : Context
        error : Exception"""

        if hasattr(ctx.command, 'on_error'):
            return
        
        ignored = (commands.CommandNotFound, commands.UserInputError)
        error = getattr(error, 'original', error)
        
        if isinstance(error, ignored):
            return

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
            except:
                pass

        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

def setup(bot):
    bot.add_cog(Checks(bot))
