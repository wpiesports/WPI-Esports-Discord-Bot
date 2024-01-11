import discord
import typing

from discord.ext import commands


async def yes_no_helper(bot: commands.Bot, ctx: commands.Context):
    """
    Waits for a yes or no response for the user
    """
    while True:
        def check_author(m):
            return m.author.id == ctx.author.id

        response = await bot.wait_for('message', check=check_author)

        if response.content.lower() == 'y' or response.content.lower() == 'yes':
            return True
        elif response.content.lower() == 'n' or response.content.lower() == 'no':
            return False
        else:
            await ctx.send('Did not recognize your response. Make sure it is a yes or a no.')


class Messaging(commands.Cog):
    """
    Messaging tools
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    @commands.check_any(commands.has_permissions(administrator=True), commands.is_owner())
    async def echo(self, ctx: commands.Context, channel: discord.TextChannel, *, msg: typing.Optional[str]):
        """
        Forwards message / attachments appended to the command to the given channel
        Usage: .echo <channel> <message>
        """
        # Check for attachments to forward
        attachments = []
        if len(ctx.message.attachments) > 0:
            for i in ctx.message.attachments:
                attachments.append(await i.to_file())

        mention_perms = discord.AllowedMentions.none()

        # Check for user mentions
        if len(ctx.message.mentions) > 0:
            # Check if users are to be pinged
            users = " ".join([x.mention for x in ctx.message.mentions])
            await ctx.send(
                f'This message mentions {users} - would you like it to ping them? (Y/N)',
                allowed_mentions=mention_perms
            )

            if await yes_no_helper(self.bot, ctx):
                mention_perms.users = True

        # Check for role mentions
        if len(ctx.message.role_mentions) > 0:
            roles = " ".join([x.mention for x in ctx.message.role_mentions])
            await ctx.send(
                f'This message mentions {roles} - would you like it to ping them? (Y/N)',
                allowed_mentions=mention_perms
            )

            if await yes_no_helper(self.bot, ctx):
                mention_perms.roles = True

        # Check for @everyone and @here mentions
        if ctx.message.mention_everyone:
            if ctx.author.guild_permissions.mention_everyone:
                await ctx.send(
                    'This message mentions @here or @everyone - would you like it to ping those? (Y/N)',
                    allowed_mentions=mention_perms
                )

                if await yes_no_helper(self.bot, ctx):
                    mention_perms.everyone = True

        if msg is not None:
            message = await channel.send(msg, files=attachments, allowed_mentions=mention_perms)
            await ctx.send(
                f'Message sent (<{message.jump_url}>)',
            )
        elif len(attachments) > 0:
            message = await channel.send(files=attachments)
            await ctx.send(
                f'Message sent (<{message.jump_url}>)',
            )
        else:
            await ctx.send('No content to send.')

    @commands.command(aliases=['echoEdit', 'editEcho'])
    @commands.check_any(commands.has_permissions(administrator=True), commands.is_owner())
    async def echo_edit(self, ctx: commands.Context, bot_msg: discord.Message, *, msg):
        """
        Edits a message sent by the bot with the message given
        """
        # Check if Gompei is author of the message
        if bot_msg.author.id != self.bot.user.id:
            await ctx.send('Cannot edit a message that is not my own')
        else:
            await bot_msg.edit(content=msg)
            await ctx.send(
                f'Message edited (<{bot_msg.jump_url}>)'
            )

    @commands.command(aliases=['echoDelete', 'deleteEcho'])
    @commands.check_any(commands.has_permissions(administrator=True), commands.is_owner())
    async def echo_delete(self, ctx: commands.Context, bot_msg: discord.Message):
        """
        Deletes a message sent by the bot
        """
        if bot_msg.author.id != self.bot.user.id:
            await ctx.send('Cannot delete a message that is not my own')
        else:
            await bot_msg.delete()
            await ctx.send(
                f'Message deleted (<{bot_msg.jump_url}>)'
            )

    @echo.error
    @echo_edit.error
    @echo_delete.error
    async def echo_error_handler(self, ctx: commands.Context, error: discord.DiscordException):
        """
        Error handling for echo commands
        """
        print(error)
        if isinstance(error.original, discord.HTTPException):
            await ctx.send('This message is too long')


async def setup(bot: commands.Bot):
    await bot.add_cog(Messaging(bot))
