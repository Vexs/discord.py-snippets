import discord
from discord.ext import commands

class Debug:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def scrape_emoji(self, ctx):
        """Grabs all emojis from all guilds the bot is in, and sends them in an emojis.zip file."""
        import io
        import zipfile
        import aiohttp

        memfile = io.BytesIO()
        zip = zipfile.ZipFile(memfile, 'w')

        with ctx.typing():
            for guild in ctx.bot.guilds:
                guildname = guild.name.replace("/", "") # may require more replacing
                for emoji in guild.emojis:
                    async with aiohttp.ClientSession(loop=ctx.bot.loop).get(emoji.url) as resp:
                        if resp.status == 200:
                            data = await resp.read()
                            extension = emoji.url.split('.')[-1]
                            emojiname = 'emojis/{guildname}/{emoji.name}.{extension}'.format(guildname=guildname, emoji=emoji, extension=extension)

                            # check if this guild has multiple of the same emoji name, and rename them accordingly
                            multiple_num = 0
                            while emojiname in zip.namelist():
                                multiple_num += 1
                                emojiname = 'emojis/{guildname}/{emoji.name}~{multiple_num}.{extension}'.format(guildname=guildname, emoji=emoji, multiple_num=multiple_num, extension=extension)
                            zip.writestr(emojiname, data)
                        else:
                            raise commands.BadArgument('Received error code {error_id} while fetching emojis.'.format(error_id=resp.status))
        zip.close()

        memfile.seek(0)
        await ctx.send(file=discord.File(memfile, filename='emojis.zip'))

def setup(bot):
    bot.add_cog(Debug(bot))
