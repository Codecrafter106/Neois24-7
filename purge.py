import discord
from discord.ext import commands

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='Neo ', intents=intents)

@bot.command(name='purge')
@commands.has_permissions(manage_messages=True)
async def purge_messages(ctx, amount: int):
    """
    Purge a specified number of messages in the current channel.
    Usage: Neo urge <amount>
    """
    # Check if the amount is within a reasonable range
    if 1 <= amount <= 100:
        # Delete messages
        await ctx.channel.purge(limit=amount + 1)  # The limit is set to 'amount + 1' to include the command itself
        await ctx.send(f'Successfully purged {amount} messages.')
    else:
        await ctx.send('Please specify a number between 1 and 100 for the amount to purge.')

# Your other commands and bot setup...
