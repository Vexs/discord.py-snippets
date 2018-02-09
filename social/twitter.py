import discord
import aiohttp
from peony import PeonyClient, events

# At the end of setup, this Cog will stream your bot's Twitter home timeline to a Discord channel using a Webhook as they are tweeted.

# Setup steps:
# Install the "peony-twitter[all]" package using "pip install peony-twitter[all]" (or pip3)
# Make a Twitter account for your bot, and follow whatever accounts you'd like.
# Get your api keys and access tokens. You'll have to make an app out of it. https://apps.twitter.com/
# Plug your keys and tokens into the KEYS dict below.
# Make a dedicated Discord channel for the incoming stream.
# Add a Webhook to that channel, and plug your Webhook ID and Token into the TWITTER_WEBHOOK tuple below.
# Add the cog to your bot, and it's good to go!

# Notes:
# This functionality is a bit useless if you're following private accounts.
# This will NOT work as-is. This is intentional.

# Import & .gitignore these if your bot is open source
KEYS = dict(
    consumer_key='<your_consumer_key>',
    consumer_secret='<your_consumer_secret>',
    access_token='<your_access_token>',
    access_token_secret='<your_access_token_secret>'
)

TWITTER_WEBHOOK = (ID_INT, 'TOKEN')

class Twitter:
    def __init__(self, bot):
        self.bot = bot
        self.twitter_client = PeonyClient(**KEYS, loop=self.bot.loop)
        self.twitter_session = aiohttp.ClientSession(loop=self.bot.loop)
        self.task = self.bot.loop.create_task(self.run())

    def __unload(self):
        self.task.cancel()

    async def run(self):
        await self.bot.wait_until_ready()
        async with self.twitter_client.userstream.user.get() as stream:
            async for data in stream:
                if events.on_tweet(data):
                    await self.webhook.send('https://twitter.com/{data.user.screen_name}/status/{data.id}'.format(data=data))

    @property
    def webhook(self):
        # webhooks are scary, so here's the comprehensive documentation:
        # http://discordpy.readthedocs.io/en/rewrite/api.html#webhook-support
        wh_id, wh_token = TWITTER_WEBHOOK
        hook = discord.Webhook.partial(id=wh_id, token=wh_token, adapter=discord.AsyncWebhookAdapter(self.twitter_session))
        return hook

def setup(bot):
    bot.add_cog(Twitter(bot))
