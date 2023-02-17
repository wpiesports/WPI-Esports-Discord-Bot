import time

import discord

from discord import app_commands
from discord.ext import commands
from typing import Optional, Union


class Utility(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot

    @app_commands.command(name='ping')
    async def ping(self, interaction: discord.Interaction) -> None:
        """
        Sends the total latency and websock latency
        """
        start = time.perf_counter()
        await interaction.response.send_message(
            embed=discord.Embed(title='Pinging...', color=discord.Color.yellow(), timestamp=discord.utils.utcnow()),
            ephemeral=True
        )
        end = time.perf_counter()
        duration = (end - start) * 1000

        await interaction.edit_original_response(
            embed=discord.Embed(
                title='Pong!',
                color=discord.Color.green(),
                description=f'Total Latency: `{round(duration, 2)} ms`\nWebSocket Latency: `{round(self.bot.latency * 1000, 2)} ms`',
                timestamp=discord.utils.utcnow()
            )
        )

    def get_nested_command(self, name: str, guild: Optional[discord.Guild]) \
            -> Optional[Union[app_commands.Command, app_commands.Group]]:
        key, *keys = name.split(' ')
        command = self.bot.tree.get_command(key, guild=guild) or self.bot.tree.get_command(key)

        for key in keys:
            if command is None:
                return None
            if isinstance(command, app_commands.Command):
                break

            command = command.get_command(key)

        return command

    @app_commands.command(name='help')
    async def help(self, interaction: discord.Interaction, command: Optional[str]):
        """
        Provides information about commands
        """
        # Generic information
        if command is None:
            embed = discord.Embed(
                title=self.bot.user.name,
                color=discord.Color.green(),
                description=f'{self.bot.description}\n\n For specific command help use `/help <command>`',
                timestamp=discord.utils.utcnow()
            )
            embed.set_footer(text='Creator: Moelandblue#0909')
            embed.set_thumbnail(url=self.bot.user.avatar.url)
        else:
            cmd = self.get_nested_command(command, guild=interaction.guild)
            if cmd is None:
                await interaction.response.send_message(f'Could not find a command named {command}', ephemeral=True)
                return

            description = (cmd.callback.__doc__ or cmd.description if isinstance(cmd, app_commands.Command) else cmd.__doc__ or cmd.description)
            embed = discord.Embed(title=cmd.qualified_name, description=description)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @commands.command(name='kill')
    @commands.has_permissions(administrator=True)
    async def shutdown(self, ctx):
        """
        Shuts down the bot
        """
        await ctx.send('Shutting down')
        await self.bot.close()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Utility(bot))
