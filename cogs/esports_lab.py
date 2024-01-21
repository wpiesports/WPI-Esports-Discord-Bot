import datetime
import json
import time

import discord

from discord.ext import commands, tasks

computers = [
    'blitzcrank',
    'dominus',
    'gibraltar',
    'hibana',
    'jett',
    'lesion',
    'mercy',
    'octane',
    'orianna',
    'reinhardt',
    'sage',
    'wraith'
]


class EsportsLab(commands.Cog):
    """
    Real time esports lab information reporting
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.activity_message = None
        self.lab_info = None

    async def load_info(self):
        """
        Loads esports lab info
        """
        try:
            with open('esports_lab.json', 'r+') as lab_info:
                data = lab_info.read()
                self.lab_info = json.loads(data)
                # Default settings

        except FileNotFoundError:
            with open('esports_lab.json', 'w+') as lab_info:
                default = {
                    'online': False,
                    'lastInput': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(0))
                }

                self.lab_info = {
                    'computers': {n: default for n in computers},
                    'discord': {
                        'server': None,
                        'channel': None,
                        'message': None
                    }
                }
                await self.save_info()

    async def save_info(self):
        """
        Saves esports lab info
        """
        with open('esports_lab.json', 'w+') as lab_info:
            lab_info.write(json.dumps(self.lab_info, indent=4))

    async def generate_activity(self):
        """
        Generates the lab activity embed
        """
        layout = [
            ['reinhardt', 'octane'],
            ['dominus', 'mercy'],
            ['jett', 'sage'],
            ['hibana', 'lesion'],
            ['orianna', 'blitzcrank'],
            ['gibraltar', 'wraith']
        ]

        embed = discord.Embed(title='Lab Activity', color=discord.Color.green())
        inactive = active = offline = 0
        for row in layout:
            for computer in row:
                info = self.lab_info['computers'][computer]
                if info['online']:

                    if False: # TODO Compare times
                        active += 1
                    else:
                        embed.add_field(name=f'<:Inactive:1196842435809124524> {computer.title()}', value=f'Available', inline=True)
                        inactive += 1

                else:
                    embed.add_field(name=f'<:Offline:1196842438338285729> {computer.title()}', value=f'Offline', inline=True)
                    offline += 1

        embed.description = f'<:Inactive:1196842435809124524> {inactive} Computers Available\n<:Active:1196842433330290728> {active} Computers In Use\n<:Offline:1196842438338285729> {offline} Offline'
        embed.timestamp = datetime.datetime.now()

        return embed

    @commands.command(name='setupLabReporting')
    @commands.check_any(commands.has_permissions(administrator=True), commands.is_owner())
    async def setup_lab_reporting(self, ctx: commands.Context, channel: discord.TextChannel):
        """
        Sets up the esports lab reporting message and channel
        """

        self.activity_message = await channel.send(embed=(await self.generate_activity()))
        self.lab_info['discord']['server'] = ctx.guild.id
        self.lab_info['discord']['channel'] = ctx.channel.id
        self.lab_info['discord']['message'] = self.activity_message.id

        await self.save_info()

    @commands.Cog.listener()
    async def on_ready(self):
        await self.load_info()

        # Loads the channel and messages used for the esports lab
        if self.lab_info['discord']['server'] is not None:
            guild = await self.bot.fetch_guild(self.lab_info['discord']['server'])
            channel = await guild.fetch_channel(self.lab_info['discord']['channel'])
            self.activity_message = await channel.fetch_message(self.lab_info['discord']['message'])

        self.update_activity.start()

    @tasks.loop(seconds=5.0)
    async def update_activity(self):
        pass


async def setup(bot: commands.Bot):
    cog = EsportsLab(bot)
    await bot.add_cog(cog)
