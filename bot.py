import asyncio
import os
import sys
import traceback

import aiohttp
import discord

from discord.ext import commands

# Initialize bot
intents = discord.Intents.default()
intents.messages = intents.message_content = intents.guild_messages = True
bot = commands.Bot(command_prefix=".", case_insensitive=True, intents=intents)
bot.remove_command("help")


# Load default events
@bot.event
async def on_ready():
    """
    Loads default settings
    """
    await bot.change_presence(activity=discord.Game(name="esports", start=discord.utils.utcnow()))
    print("Logged on as {0}".format(bot.user))


@bot.event
async def on_command_error(ctx, error):
    """
    Default error handling for the bot

    :param ctx: context object
    :param error: error
    """
    if isinstance(error, commands.CheckFailure) or isinstance(error, commands.MissingPermissions):
        print("!ERROR! " + str(ctx.author.id) + " did not have permissions for " + ctx.command.name + " command")
    elif isinstance(error, commands.BadArgument):
        argument = list(ctx.command.clean_params)[len(ctx.args[2:] if ctx.command.cog else ctx.args[1:])]
        await ctx.send("Could not find the " + argument)
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(ctx.command.name + " is missing arguments")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("Bot is missing permissions.")
    else:
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


# Run the bot
async def main():
    async with aiohttp.ClientSession() as session:
        async with bot:
            bot.session = session
            await bot.start(os.environ['DISCORD_TOKEN'])


asyncio.run(main())
