import discord
from discord.ext import commands

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='Neo ', intents=intents)

# Define a dictionary of color names and their hex codes
color_codes = {
    "Red": "#FF0000",
    "Green": "#00FF00",
    "Blue": "#0000FF",
    "Orange":"#FFA500",
    "Purple":"#800080",
    "Neon Green":"#39FF14",
    "Black":"#000000",
    "Pink":"#FFC0CB",
    "Cyan":"#00FFFF",
    "DarkBlue":"#00008B",
    "LightBlue":"#ADD8E6",
    "Yellow":"#FFFF00",
    "Magenta":"#FF00FF"
    # Add more colors as needed
}

@bot.command(name='colorcode')
async def color_code(ctx):
    # Check if the command invoker has the 'manage_messages' permission (modify this based on your requirements)
    if ctx.message.author.guild_permissions.manage_messages:
        # Create an embed to display the color codes
        embed = discord.Embed(
            title='Color Codes',
            description='\n'.join([f'{color_name}: {hex_code}' for color_name, hex_code in color_codes.items()]),
            color=discord.Color.dark_purple()
        )

        # Send the color codes in the same channel
        await ctx.send(embed=embed)
    else:
     await ctx.send("You don't have the necessary permissions to use this command.")

# Your other commands and bot setup...

