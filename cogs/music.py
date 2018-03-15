import math
import re

import discord
from discord.ext import commands
import lavalink

time_rx = re.compile('[0-9]+')


class Music:
    def __init__(self, bot):
        self.bot = bot
        lavalink.Client(bot=bot, password=bot.config.lavalink, port=8080, loop=self.bot.loop, log_level='debug')
        self.bot.lavalink.client.register_hook(self.track_hook)

    async def track_hook(self, player, event):
        if event == 'TrackStartEvent':
            c = player.fetch('channel')
            if c:
                c = self.bot.get_channel(c)
                if c:
                    embed = discord.Embed(colour=c.guild.me.top_role.colour, title='Now Playing', description=player.current.title)
                    embed.set_thumbnail(url=player.current.thumbnail)
                    await c.send(embed=embed)
        elif event == 'QueueEndEvent':
            c = player.fetch('channel')
            if c:
                c = self.bot.get_channel(c)
                if c:
                    await c.send('Queue ended! Leaving channel.')
                    await player.disconnect()


    @commands.command(aliases=['p'])
    async def play(self, ctx, *, query):
        '''Plays a song.'''
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if player.paused:
            await player.set_pause(False)
            return await ctx.send('⏯ | Resumed')

        if not player.is_connected:
            if not ctx.author.voice or not ctx.author.voice.channel:
                return await ctx.send('You need to be in a voice channel to play songs!')

            permissions = ctx.author.voice.channel.permissions_for(ctx.me)

            if not permissions.connect or not permissions.speak:
                return await ctx.send('Missing permissions `CONNECT` and/or `SPEAK`.')

            player.store('channel', ctx.channel.id)
            await player.connect(ctx.author.voice.channel.id)
        else:
            if not ctx.author.voice or not ctx.author.voice.channel or player.connected_channel.id != ctx.author.voice.channel.id:
                return await ctx.send('You need to be in my voice channel!')

        query = query.strip('<>')

        if not query.startswith('http'):
            query = f'ytsearch:{query}'

        tracks = await self.bot.lavalink.client.get_tracks(query)

        if not tracks:
            return await ctx.send('Nothing found 👀')

        embed = discord.Embed(colour=ctx.guild.me.top_role.colour)

        if 'list' in query and 'ytsearch:' not in query:
            for track in tracks:
                player.add(requester=ctx.author.id, track=track)

            embed.title = "Playlist Added to Queue"
            embed.description = f"Imported {len(tracks)} tracks from the playlist :)"
            await ctx.send(embed=embed)
        else:
            embed.title = "Track Added to Queue"
            embed.description = f'[{tracks[0]["info"]["title"]}]({tracks[0]["info"]["uri"]})'
            await ctx.send(embed=embed)
            player.add(requester=ctx.author.id, track=tracks[0])

        if not player.is_playing:
            await player.play()

    @commands.command()
    async def seek(self, ctx, time):
        '''Seek to a part of the song.'''
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send('Not playing.')

        pos = '+'
        if time.startswith('-'):
            pos = '-'

        seconds = time_rx.search(time)

        if not seconds:
            return await ctx.send('You need to specify the amount of seconds to skip!')

        seconds = int(seconds.group()) * 1000

        if pos == '-':
            seconds = seconds * -1

        track_time = player.position + seconds

        await player.seek(track_time)

        await ctx.send(f'Moved track to **{lavalink.Utils.format_time(track_time)}**')

    @commands.command(aliases=['forceskip', 'fs'])
    async def skip(self, ctx):
        '''Skip the current song'''
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send('Not playing.')

        await ctx.send('⏭ | Skipped.')
        await player.skip()

    @commands.command()
    async def stop(self, ctx):
        '''Stops the player and disconnects.'''
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_connected:
            return await ctx.send('Not playing.')

        if player.is_playing:
            player.queue.clear()
            await player.stop()
        await ctx.send('⏹ | Stopped.')
        await player.disconnect()

    @commands.command(aliases=['np', 'n'])
    async def now(self, ctx):
        '''Shows the currently playing song.'''
        player = self.bot.lavalink.players.get(ctx.guild.id)
        song = 'Nothing'

        if player.current:
            pos = lavalink.Utils.format_time(player.position)
            if player.current.stream:
                dur = 'LIVE'
            else:
                dur = lavalink.Utils.format_time(player.current.duration)
            song = f'**[{player.current.title}]({player.current.uri})**\n({pos}/{dur})'

        embed = discord.Embed(colour=ctx.guild.me.top_role.colour, title='Now Playing', description=song)
        await ctx.send(embed=embed)

    @commands.command(aliases=['q'])
    async def queue(self, ctx, page: int=1):
        '''Shows the current queue.'''
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.queue:
            return await ctx.send('There\'s nothing in the queue! Why not queue something?')

        items_per_page = 10
        pages = math.ceil(len(player.queue) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue_list = ''

        for i, track in enumerate(player.queue[start:end], start=start):
            queue_list += f'`{i + 1}.` [**{track.title}**]({track.uri})\n'

        embed = discord.Embed(colour=ctx.guild.me.top_role.colour,
                              description=f'**{len(player.queue)} tracks**\n\n{queue_list}')
        embed.set_footer(text=f'Viewing page {page}/{pages}')
        await ctx.send(embed=embed)

    @commands.command(aliases=['resume', 'unpause'])
    async def pause(self, ctx):
        '''Pause/Resume the current song.'''
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send('Not playing.')

        if player.paused:
            await player.set_pause(False)
            await ctx.send('⏯ | Resumed')
        else:
            await player.set_pause(True)
            await ctx.send('⏯ | Paused')

    @commands.command(aliases=['vol'])
    async def volume(self, ctx, volume: int=None):
        '''Set the volume of the player.'''
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not volume:
            return await ctx.send(f'🔈 | {player.volume}%')

        await player.set_volume(volume)
        await ctx.send(f'🔈 | Set to {player.volume}%')

    @commands.command()
    async def shuffle(self, ctx):
        '''Shuffle the queue.'''
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send('Nothing playing.')

        player.shuffle = not player.shuffle

        await ctx.send('🔀 | Shuffle ' + ('enabled' if player.shuffle else 'disabled'))

    @commands.command()
    async def repeat(self, ctx):
        '''Loop the queue.'''
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send('Nothing playing.')

        player.repeat = not player.repeat

        await ctx.send('🔁 | Repeat ' + ('enabled' if player.repeat else 'disabled'))

    @commands.command()
    async def remove(self, ctx, index: int):
        '''Remove a song from the queue.'''
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.queue:
            return await ctx.send('Nothing queued.')

        if index > len(player.queue) or index < 1:
            return await ctx.send('Index has to be >=1 and <=queue size')

        index = index - 1
        removed = player.queue.pop(index)

        await ctx.send('Removed **' + removed.title + '** from the queue.')

    @commands.command()
    async def find(self, ctx, *, query):
        '''Lists the first 10 songs from a search.'''
        if not query.startswith('ytsearch:') and not query.startswith('scsearch:'):
            query = 'ytsearch:' + query

        tracks = await self.bot.lavalink.client.get_tracks(query)

        if not tracks:
            return await ctx.send('Nothing found')

        tracks = tracks[:10]  # First 10 results

        o = ''
        for i, t in enumerate(tracks, start=1):
            o += f'`{i}.` [{t["info"]["title"]}]({t["info"]["uri"]})\n'

        embed = discord.Embed(colour=ctx.guild.me.top_role.colour,
                              description=o)

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Music(bot))


def teardown(bot):
    bot.lavalink.client.destroy()
