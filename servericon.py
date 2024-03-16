import discord
from discord.ext import commands

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='Neo ', intents=intents)

@bot.command(name='servericon')
async def server_icon(ctx):
    server = ctx.guild
    requester = ctx.author

    # Create the server icon embed
    embed = discord.Embed(
        title=f'{server.name} - Icon',
        color=discord.Color.dark_purple()
    )

    # Set the server icon as an image in the description
    embed.set_image(url=server.icon.url)

    # Set the footer with the requester's info
    embed.set_footer(text=f'Requested by {requester}', icon_url=requester.avatar.url if requester.avatar else discord.Embed.Empty)

    # Send the embed
    await ctx.send(embed=embed)

