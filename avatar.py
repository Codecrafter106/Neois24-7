import discord
from discord.ext import commands

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='Neo ', intents=intents)

@bot.command(name='avatar')
async def user_avatar(ctx, user: discord.Member = None):
    requester = ctx.author

    # If no user is mentioned, default to the author's avatar
    if user is None:
        user = requester

    # Create the avatar embed
    embed = discord.Embed(
        title=f'{user.name} - Avatar',
        color=discord.Color.dark_purple()
    )

    # Set the user's avatar as an image in the description
    embed.set_image(url=user.avatar.url)

    # Set the footer with the requester's info
    embed.set_footer(text=f'Requested by {requester}', icon_url=requester.avatar.url if requester.avatar else discord.Embed.Empty)

    # Send the embed
    await ctx.send(embed=embed)
