import discord
from discord.ext import commands

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='Neo ', intents=intents)

@bot.command(name='slowmode')
async def set_slowmode(ctx, duration: int, unit: str):
    # Check if the command invoker has the 'manage_messages' permission (modify this based on your requirements)
    if ctx.message.author.guild_permissions.manage_messages:
        # Convert the duration to seconds based on the provided unit
        if unit.lower() == 'min':
            duration *= 60
        elif unit.lower() != 'sec':
            await ctx.send('Invalid unit. Please use "sec" or "min".')
            return

        # Check if the duration is within the allowed range (5 seconds to 6 hours)
        if 5 <= duration <= 21600:
            # Set slowmode in the current channel
            await ctx.channel.edit(slowmode_delay=duration)

            await ctx.send(f'Slowmode set to {duration} seconds in this channel.')
        else:
            await ctx.send('Please choose a duration between 5 seconds and 6 hours.')
    else:
        await ctx.send("You don't have the necessary permissions to use this command.")

@bot.command(name='disableslowmode')
async def disable_slowmode(ctx):
    # Check if the command invoker has the 'manage_messages' permission (modify this based on your requirements)
    if ctx.message.author.guild_permissions.manage_messages:
        # Check if slow mode is already disabled
        if ctx.channel.slowmode_delay == 0:
            await ctx.send('Slowmode is already disabled in this channel.')
        else:
            # Disable slow mode in the current channel
            await ctx.channel.edit(slowmode_delay=0)
            await ctx.send('Slowmode has been disabled in this channel.')
    else:
        await ctx.send("You don't have the necessary permissions to use this command.")

# Your other commands and bot setup...
