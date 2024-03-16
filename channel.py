import discord
from discord.ext import commands

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='Neo ', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(name='createchannel', aliases=['cc'])
async def create_channel(ctx, *args):
    if ctx.message.author.guild_permissions.manage_channels:
        guild = ctx.guild
        params = [arg.strip().lower() for arg in " ".join(args).split('|')]
        name, channel_type = params[0], params[1] if len(params) > 1 else 'text'
        category_name = params[2] if len(params) > 2 else None

        category_obj = None

        if category_name:
            # Check if the specified category exists (case-insensitive)
            for existing_category in guild.categories:
                if existing_category.name.lower() == category_name:
                    category_obj = existing_category
                    break

            if category_obj is None:
                # If category does not exist, send an error message
                await ctx.send(f'Error: Category "{category_name}" does not exist.')
                return

        # Create a channel based on the specified type or default to text
        if channel_type == 'voice':
            new_channel = await guild.create_voice_channel(name, category=category_obj)
        else:
            new_channel = await guild.create_text_channel(name, category=category_obj)

        await ctx.send(f'Channel {new_channel.mention} created successfully in category {category_obj.name if category_obj else "None"}!')

    else:
        await ctx.send('You do not have the required permissions to use this command.')

@create_channel.error
async def create_channel_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please provide the necessary arguments for the command.')
    elif isinstance(error, commands.BadArgument):
        await ctx.send('Invalid argument provided. Please check your command syntax.')
    else:
        await ctx.send(f'An error occurred: {error}')

@bot.command(name='deletechannel', aliases=['dc'])
async def delete_channel(ctx, channel_name):
    if ctx.message.author.guild_permissions.manage_channels:
        guild = ctx.guild

        # Check if the specified channel exists (case-insensitive)
        target_channel = discord.utils.get(guild.channels, name=channel_name)
        if target_channel:
            # Delete the channel
            await target_channel.delete()
            await ctx.send(f'Channel "{channel_name}" deleted successfully!')
        else:
            # If channel does not exist, send an error message
            await ctx.send(f'Error: Channel "{channel_name}" does not exist.')
    else:
        await ctx.send('You do not have the required permissions to use this command.')

@delete_channel.error
async def delete_channel_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please provide the necessary arguments for the command.')
    elif isinstance(error, commands.BadArgument):
        await ctx.send('Invalid argument provided. Please check your command syntax.')
    else:
        await ctx.send(f'An error occurred: {error}')
