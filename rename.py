import discord 
import asyncio
from discord.ext import commands

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='Neo ', intents=intents)

@bot.command(name='rename', aliases=['r', 'Rename', 'R', 'RENAME'])
async def rename_channel(ctx, new_name, channel: discord.TextChannel = None):
    if ctx.author.guild_permissions.manage_channels:
        if channel is None:
            channel = ctx.channel

        old_name = channel.name  # Save the old channel name

        try:
            await channel.edit(name=new_name)
            await ctx.send(f"Channel name of {old_name} has been changed to {new_name}")
        except discord.Forbidden:
            await ctx.send("I don't have the required permissions to rename the channel.")
        except discord.HTTPException as e:
            if e.status == 429:  # Rate limit error
                retry_after = e.retry_after
                await asyncio.sleep(retry_after)
                await ctx.invoke(rename_channel, new_name=new_name, channel=channel)
            else:
                await ctx.send(f"An error occurred: {e}")
    else:
        await ctx.send("You don't have the necessary permissions to use this command.")
