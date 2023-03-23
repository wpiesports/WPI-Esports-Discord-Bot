import json
import os

import discord
import requests

from discord.ext import commands, tasks


def refresh_twitch_credentials():
    """
    Refreshes twitch credentials

    :return: New twitch credentials
    """
    response = requests.post(
        url='https://id.twitch.tv/oauth2/token',
        params={
            'client_id': os.environ['TWITCH_CLIENT_ID'],
            'client_secret': os.environ['TWITCH_CLIENT_SECRET'],
            'grant_type': 'client_credentials'
        }
    )
    if response.status_code != 200:
        return None

    return json.loads(response.content)


class Streaming(commands.Cog):
    """
    Tools for streaming updates
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        if 'TWITCH_CLIENT_ID' not in os.environ or 'TWITCH_CLIENT_SECRET' not in os.environ:
            print('Unloaded cog Streaming - are your twitch credentials setup properly?')
            self.bot.unload_extension('cogs.Streaming')
            self.twitch_credentials = None
            return

        self.twitch_credentials = refresh_twitch_credentials()
        self.current_stream = None
        self.message = None
        self.twitch_update.start()

    @tasks.loop(seconds=120)
    async def twitch_update(self):
        """
        Checks for WPI Esports Twitch updates every 2 minutes
        """
        twitch_data = json.loads(
            requests.get(
                'https://api.twitch.tv/helix/streams?user_id=28043034',
                headers={
                    'client-id': os.environ['TWITCH_CLIENT_ID'],
                    'Authorization': f"Bearer {self.twitch_credentials['access_token']}"
                }
            ).content
        )['data']

        if len(twitch_data) > 0:
            twitch_data = twitch_data[0]
            await self.bot.change_presence(activity=discord.Streaming(
                    name=twitch_data['title'],
                    url='https://www.twitch.tv/WPIEsports',
                    twitch_name='WPIEsports'
                )
            )

            # if self.current_stream is None:
            #     stream_channel = self.bot.get_guild(197532699999731712).get_channel(858354299196669983)
            #     self.current_stream = discord.Embed(
            #         title=twitch_data["title"],
            #         colour=discord.Colour(0x6441a5),
            #         description=f"Streaming {twitch_data['game_name']} for {twitch_data['viewer_count']} viewers\n"
            #                     f"[Watch Stream](https://www.twitch.tv/{twitch_data['user_name']})",
            #         url=f"https://www.twitch.tv/{twitch_data['user_name']}",
            #     )
            #     self.current_stream.set_image(url=twitch_data['thumbnail_url'].format(width='1920', height='1080'))
            #
            #     user_data = json.loads(
            #         requests.get(
            #             'https://api.twitch.tv/helix/users?id=28043034',
            #             headers={
            #                 'client-id': os.environ['TWITCH_CLIENT_ID'],
            #                 'Authorization': f"Bearer {self.twitch_credentials['access_token']}"
            #             }
            #
            #         ).content
            #     )['data'][0]
            #
            #     self.current_stream.set_author(
            #         name='WPI Esports',
            #         url=f"https://www.twitch.tv/{twitch_data['user_name']}",
            #         icon_url=user_data['profile_image_url']
            #     )
            #     self.current_stream.timestamp = discord.utils.utcnow()
            #
            #     self.message = await stream_channel.send(
            #         'WPI Esports is now streaming! Check it out <@&858347098691993630>',
            #         embed=self.current_stream
            #     )
            # else:
            #     # Update viewers / game / title / thumbnail
            #     self.current_stream.title = twitch_data["title"]
            #     self.current_stream.description = f"Streaming {twitch_data['game_name']} for " \
            #                                       f"{twitch_data['viewer_count']} viewers\n" \
            #                                       f"[Watch Stream](https://www.twitch.tv/{twitch_data['user_name']})"
            #     self.current_stream.set_image(url=twitch_data['thumbnail_url'].format(width='1920', height='1080'))
            #     await self.message.edit(embed=self.current_stream)
        else:
            await self.bot.change_presence(activity=discord.Game(name='esports', start=discord.utils.utcnow()))
            self.current_stream = None

    @twitch_update.before_loop
    async def before_twitch_update(self):
        """
        Checks to see if credentials loaded properly, if not unloads the cog
        """
        await self.bot.wait_until_ready()
        if self.twitch_credentials is None:
            print('Invalid twitch credentials, unloading Streaming cog')
            self.bot.unload_extension('cogs.Streaming')
            self.twitch_update.cancel()


async def setup(bot: commands.Bot):
    await bot.add_cog(Streaming(bot))
