import discord
from discord.ext import commands

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='Neo ', intents=intents)

@bot.command(name='serverinfo')
async def server_info(ctx):
    server = ctx.guild
    requester = ctx.author

    # Get the server avatar URL
    server_avatar = server.icon if server.icon else discord.Embed.Empty

    # Filter out bots from the member count
    real_members_count = sum(not member.bot for member in server.members)

    # Create the server info embed
    embed = discord.Embed(title=f'Server Information', description=f'**Server Name:** {server.name}', color=discord.Color.dark_purple())
    embed.set_thumbnail(url=server_avatar)

    # Add server details to the embed
    embed.add_field(name='Server ID', value=server.id, inline=True)
    embed.add_field(name='Owner', value=server.owner, inline=True)

    # Check if server.region is available
    if hasattr(server, 'region'):
        embed.add_field(name='Region', value=str(server.region).capitalize(), inline=True)

    embed.add_field(name='Members', value=real_members_count, inline=True)
    embed.add_field(name='Text Channels', value=len(server.text_channels), inline=True)
    embed.add_field(name='Voice Channels', value=len(server.voice_channels), inline=True)
    embed.add_field(name='Roles', value=len(server.roles), inline=True)

    # Set the footer with the requester's info
    embed.set_footer(text=f'Requested by {requester}', icon_url=requester.avatar)

    # Send the embed
    await ctx.send(embed=embed)
