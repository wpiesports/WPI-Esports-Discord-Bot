import asyncio
import os
import sys
import traceback

import aiohttp
import discord

from discord.ext import commands
from discord.ext.commands import Greedy
from typing import Optional, Literal


# Initialize bot
intents = discord.Intents.default()
intents.messages = intents.message_content = intents.guild_messages = True
bot = commands.Bot(command_prefix='!', case_insensitive=True, intents=intents)
bot.remove_command('help')
default_cogs = ['utility']


# Cog handlers
@bot.group(name='cogs', aliases=['c'])
@commands.is_owner()
async def cogs(ctx: commands.Context):
    """
    Command group for managing cogs
    """


@cogs.command(name='load')
async def load_cog(ctx: commands.Context, cog: str):
    """
    Loads a cog from the cogs directory
    """
    await bot.load_extension(f'cogs.{cog.lower()}')
    await ctx.send(f'Successfully added cog {cog.title()}')


@cogs.command(name='unload')
async def unload_cog(ctx: commands.Context, cog: str):
    """
    Unloads a cog
    """
    await bot.unload_extension(f'cogs.{cog.lower()}')
    await ctx.send(f'Successfully removed cog {cog.title()}')


@cogs.command(name='reload')
async def reload_cog(ctx: commands.Context, cog: str):
    """
    Reloads a cog
    """
    await bot.unload_extension(f'cogs.{cog.lower()}')
    await bot.load_extension(f'cogs.{cog.lower()}')
    await ctx.send(f'Successfully reloaded cog {cog.title()}')


@cogs.command(name='list')
async def list_cogs(ctx: commands.Context):
    """
    Lists the cogs available and their current status
    """
    await ctx.send(f'__Loaded Cogs__\n{os.linesep.join([x.title() for x in bot.extensions])}')


# Command syncing
@bot.command()
@commands.guild_only()
@commands.is_owner()
async def sync(ctx: commands.Context, guilds: Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
    """
    Syncs the command tree, Umbras sync command
    """
    if not guilds:
        # Sync current guild
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        # Copy global commands to this guild
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        # Clears commands from current guild
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()

        await ctx.send(f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}")
        return

    count = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            count += 1

    await ctx.send(f"Synced the tree to {count}/{len(guilds)}.")


@cogs.error
@load_cog.error
@unload_cog.error
@reload_cog.error
@list_cogs.error
async def cogs_error_handler(ctx: commands.Context, error: discord.DiscordException):
    """
    Error handling for cog commands
    """
    if isinstance(error.original, commands.ExtensionAlreadyLoaded):
        await ctx.send('This cog is already loaded')
    elif isinstance(error.original, commands.ExtensionNotLoaded):
        await ctx.send('This cog is not loaded')
    elif isinstance(error.original, commands.ExtensionNotFound):
        await ctx.send('Could not find a cog with that name')
    elif isinstance(error.original, commands.ExtensionFailed):
        await ctx.send('Failed to load the cog')


# Load default events
@bot.event
async def on_ready():
    """
    Loads default settings
    """
    await bot.change_presence(activity=discord.Game(name='esports', start=discord.utils.utcnow()))
    print("Logged on as {0}".format(bot.user))


# Error Handling
@bot.event
async def on_command_error(ctx: commands.Context, error: discord.DiscordException):
    """
    Default error handling for the bot

    :param ctx: context object
    :param error: error
    """
    if isinstance(error, commands.CheckFailure) or isinstance(error, commands.MissingPermissions):
        print(f'!ERROR! {ctx.author.id} did not have permissions for {ctx.command.name} command')
    elif isinstance(error, commands.BadArgument):
        argument = list(ctx.command.clean_params)[len(ctx.args[2:] if ctx.command.cog else ctx.args[1:])]
        await ctx.send(f'Could not find the {argument}')
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'{ctx.command.name} is missing arguments')
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send('Bot is missing permissions.')
    else:
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


# Run the bot
async def main():
    async with aiohttp.ClientSession() as session:
        async with bot:
            # Load default cogs
            for cog in default_cogs:
                await bot.load_extension(f'cogs.{cog}')
                print(f'Loaded cog {cog}')

            bot.session = session
            await bot.start(os.environ['DISCORD_TOKEN'])


asyncio.run(main())
