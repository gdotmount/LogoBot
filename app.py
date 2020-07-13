import discord
client=discord.Client
class MyClient(client):
    async def on_message(self, message):
        if message.author == self.user:
            return
        if message.content.startswith('hello'):
            await message.channel.send('hello there')

from discord.ext import commands
bot = commands.Bot(command_prefix='#')
@bot.command
async def beep(ctx):
    await ctx.channel.send('boop')

client.run('NjkyNDUzMzkxMDkxMzY4MDE3.XwwdKg.U_r_huoQ-FpZ-POZ9C9MGRZnqoA')