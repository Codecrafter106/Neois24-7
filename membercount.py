import discord
from discord.ext import commands

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='Neo ', intents=intents)

@bot.command(name='membercount', aliases=['mc'])
async def member_count(ctx):
    server = ctx.guild
    requester = ctx.author

    # Count real members and bots
    real_members_count = sum(not member.bot for member in server.members)
    bots_count = sum(member.bot for member in server.members)
    total_members_count = len(server.members)

    # Create the member count embed
    embed = discord.Embed(title=f'Member Count', color=discord.Color.dark_purple())

    # Set the thumbnail as the server's icon
    embed.set_thumbnail(url=server.icon if server.icon else discord.Embed.Empty)
    
    # Add breakdown information to the description
    embed.description = f'**Real Members:** {real_members_count}\n**Bots:** {bots_count}\n**Total Members:** {total_members_count}'

    # Set the footer with the requester's info
    embed.set_footer(text=f'Requested by {requester}', icon_url=requester.avatar if requester.avatar else discord.Embed.Empty)

    # Send the embed
    await ctx.send(embed=embed)
