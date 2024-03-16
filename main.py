from dotenv import load_dotenv
from flask import Flask
import os
import asyncio
import datetime 
import requests
import random
import sqlite3
import discord
from discord.ext import commands, tasks
from purge import purge_messages  # Import the purge command 
from Neo import bot, check_balance, daily, coinflip, pay, leaderboard, Neocustom_help, add_neo, slots, bank_deposit, bank_withdraw, bank_balance
from roles import add_role, del_role, assign_role
from tenor import tenor_search, giphy
from warning import issue_warning
from color import color_code
from slowmode import set_slowmode, disable_slowmode
from serverinfo import server_info
from membercount import member_count
from servericon import server_icon
from avatar import user_avatar
from rename import rename_channel
from channel import create_channel, delete_channel
intents = discord.Intents.all()

# Access the bot token from the environment variable
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

if TOKEN is None:
    raise ValueError("DISCORD_BOT_TOKEN environment variable not set")


bot = commands.Bot(command_prefix=['Neo ', 'N ', 'neo ', 'n ', 'NEO ', 'Neo', 'N', 'neo', 'n','NEO', 'Neo', 'N','neo', ], intents=intents)

tickets = {}  
# Define your commands with trigger and title

# Connect to the SQLite database (create a new database if it doesn't exist)
# Connect to the SQLite database

# SQLite3 database setup
conn = sqlite3.connect('pokemon_spawn.db')
cursor = conn.cursor()
# SQLite3 database setup
cursor.execute('''
    CREATE TABLE IF NOT EXISTS pokemon_spawn (
        server_id INTEGER,
        channel_id INTEGER,
        spawn_enabled INTEGER,
        cooldown_seconds INTEGER,
        last_spawn_time TEXT,
        last_spawned_pokemon TEXT,
        last_spawned_level INTEGER  -- Add this line for the missing column
    )
''')
conn.commit()


# URL of a Pokemon names list
pokemon_list_url = 'https://raw.githubusercontent.com/sindresorhus/pokemon/master/data/en.json'
# Variable to keep track of whether the spawn task is already running
spawn_task_running = False
last_spawned_pokemon_dict = {}
# Connect to SQLite3 database
conn = sqlite3.connect('tickets.db')
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS tickets (
        user_id INTEGER PRIMARY KEY,
        channel_id INTEGER
    )
''')
conn.commit()

# Connect to SQLite database
conn = sqlite3.connect('word_blacklist.db')
cursor = conn.cursor()

# Connect to SQLite database
conn = sqlite3.connect('server_prefixes.db')
cursor = conn.cursor()

# Create the table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS server_prefixes (
        guild_id TEXT PRIMARY KEY,
        old_prefix TEXT,
        new_prefix TEXT
    )
''')
conn.commit()
# Create the table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS word_blacklist (
        guild_id TEXT,
        badword TEXT,
        PRIMARY KEY (guild_id, badword)
    )
''')
conn.commit()

commands_info = {
    'ban': {'trigger': '•Neo ban <user>', 'title': 'Ban Command'},
    'kick': {'trigger': '•Neo kick <user>', 'title': 'Kick Command'},
    'purge': {'trigger': '•Neo purge <number>', 'title': 'purge Command'}, 
'LOCKDOWN': {'trigger': '•Neo lockdown', 'title': '🔒lockdown Command'}, 
'Unlock': {'trigger': '•Neo unlock', 'title': '🔓unlock Command'},
'Neohelp': {'trigger': '•Neo nhelp', 'title': 'Neo cowoncy help page'},
'ADDROLE': {'trigger': '•Neo addrole <role> <colorhex> <hoist <true/false>>', 'title': 'Role creating command'},
'delrole': {'trigger': '•Neo delrole <role>', 'title': 'Role deleting command'},
'role': {'trigger': '•Neo role <user> <role>', 'title': 'Role assigning command'}, 
'tenor': {'trigger' : '•Neo tenor <word&phrase>', 'title': 'tennor command'}, 
'giphy': {'trigger' : '•Neo giphy <word&phrase>', 'title': 'giphy command'}, 
'issue_warning': {'trigger' : '•Neo warning <user> <reason>', 'title': 'Warn user'}, 
'Removebadword': {'trigger' : '•Neo rename <New_name> <#channel>', 'title': 'rename channel'}, 
'ColorCode': {'trigger' : '•Neo colorcode', 'title': 'Show all color hex code'}, 
'Slowmode': {'trigger' : '•Neo slowmode <duration> <sec/min>', 'title': 'Enable slowmode in one command'}, 
'disableslowmode': {'trigger' : '•Neo disableslowmode', 'title': 'Disable slowmode in one command'}, 
'Serverinfo': {'trigger' : '•Neo serverinfo', 'title': 'show server information'}, 
'Membercount': {'trigger' : '•Neo membercount,mc', 'title': 'count the members of server'},
'ServerIcon': {'trigger' : '•Neo servericon', 'title': 'Show the Icon of server'},
'panel': {'trigger' : '•Neo panel | <title> | <description>', 'title': 'Ticket panel'},
'Avatar': {'trigger' : '•Neo avatar <user>', 'title': 'show user avatar'},
'Rename': {'trigger' : '•Neo rename/r <New_name> <channel>', 'title': 'Rename the channel name'},
'Create_channel': {'trigger' : '•Neo createchannel/cc <Channel_name> | <Voice/Text> | <category>', 'title': 'Create a channel'},
'Delete_channel': {'trigger' : '•Neo deletechannel/dc <channel_name>', 'title': 'Delete a channel'},

    # Add more commands as needed
}

DEFAULT_COLOR = discord.Color.dark_purple()
# Connect to SQLite database
conn = sqlite3.connect('ticket_database.db')
cursor = conn.cursor()

# Create a table to store ticket counts for each server
cursor.execute('''CREATE TABLE IF NOT EXISTS ticket_counts (
                    server_id TEXT PRIMARY KEY,
                    count INTEGER
                  )''')
conn.commit()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

    # Fetch and set prefixes for all servers
    for guild in bot.guilds:
        guild_id = str(guild.id)
        cursor.execute('SELECT prefix FROM server_prefixes WHERE guild_id = ?', (guild_id,))
        result = cursor.fetchone()

        if result:
            server_prefix = result[0]
            bot.command_prefix = commands.when_mentioned_or(server_prefix)
        else:
            # Use the default prefix if no custom prefix is set for the server
            bot.command_prefix = 'Neo '

    print('Bot is ready.')


@bot.command(name='ban')
async def ban(ctx, member: discord.Member, *, reason=None):
    if ctx.author.guild_permissions.administrator:
        try:
            await member.ban(reason=reason)
            if reason:
                await ctx.send(f'{member.name}#{member.discriminator} has been banned. Reason: {reason}')
                await member.send(f'You have been banned from {ctx.guild.name}. Reason: {reason}')
            else:
                await ctx.send(f'{member.name}#{member.discriminator} has been banned.')
                await member.send(f'You have been banned from {ctx.guild.name}.')

        except discord.NotFound:
            await ctx.send(f'User {member.name}#{member.discriminator} not found.')
    else:
        await ctx.send("You don't have permission to use this command.")

@bot.command(name='kick')
async def kick(ctx, member: discord.Member, *, reason=None):
    if ctx.author.guild_permissions.administrator:
        try:
            await member.kick(reason=reason)
            if reason:
                await ctx.send(f'{member.name}#{member.discriminator} has been kicked. Reason: {reason}')
                await member.send(f'You have been kicked from {ctx.guild.name}. Reason: {reason}')
            else:
                await ctx.send(f'{member.name}#{member.discriminator} has been kicked.')
                await member.send(f'You have been kicked from {ctx.guild.name}.')

        except discord.NotFound:
            await ctx.send(f'User {member.name}#{member.discriminator} not found.')
    else:
        await ctx.send("You don't have permission to use this command.")

 # Remove the default help command
bot.remove_command('help')

@bot.command(name='help')
async def custom_help(ctx):
    author = ctx.author
    commands_per_page = 10

    def generate_help_embed():
        embed = discord.Embed(title=f'Help - Page 1', color=0x800080) 

        for trigger, info in commands_info.items():
            embed.add_field(name=f'{info["trigger"]}', value=f'{info["title"]}', inline=False)

        embed.set_footer(text='More commands will be added in the future.')
        return embed

    help_embed = generate_help_embed()
    await ctx.send(embed=help_embed)

@bot.command(name='ticketopen')
async def ticket_open(ctx):
    user_id = ctx.author.id

    cursor.execute('SELECT * FROM tickets WHERE user_id = ?', (user_id,))
    existing_ticket = cursor.fetchone()

    if not existing_ticket:
        # Create a private ticket channel for the user
        channel_name = f'Ticket - {ctx.author.name}'
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            ctx.guild.me: discord.PermissionOverwrite(read_messages=True)
        }
        channel = await ctx.guild.create_text_channel(channel_name, overwrites=overwrites)

        # Store ticket information in the database
        cursor.execute('INSERT INTO tickets VALUES (?, ?)', (user_id, channel.id))
        conn.commit()

        await ctx.send(f'Ticket opened by <@{user_id}>. Only the creator and administrators can interact.')

@bot.command(name='ticketclose')
async def ticket_close(ctx):
    user_id = ctx.author.id
    cursor.execute('SELECT * FROM tickets WHERE user_id = ?', (user_id,))
    ticket_info = cursor.fetchone()

    # Check if the user is an administrator
    is_admin = ctx.author.guild_permissions.administrator

    if is_admin or (ticket_info and ticket_info[1] == ctx.channel.id):
        channel = bot.get_channel(ticket_info[1])
        if channel:
            await channel.send('Ticket closed.')
            await channel.delete()

            # Remove ticket information from the database
            cursor.execute('DELETE FROM tickets WHERE user_id = ?', (user_id,))
            conn.commit()
        else:
            await ctx.send('Error: Unable to close the ticket. Channel not found.')
    else:
        await ctx.send('Error: You do not have permission to close this ticket.')

@bot.command(name='lockdown')
async def lockdown(ctx):
    # Check if the user issuing the command is an administrator
    if ctx.message.author.guild_permissions.administrator:
        channel = ctx.channel

        # Disable send message permission for @everyone role
        await channel.set_permissions(ctx.guild.default_role, send_messages=False)

        # Unique response with embed
        embed = discord.Embed(
            title='Lockdown Initiated! :lock:',
            description='This channel has been sealed. No messages shall pass! :no_entry_sign:',
            color=discord.Color.dark_purple()
        )
        await ctx.send(embed=embed)
    else:
        # Unique response with embed
        embed = discord.Embed(
            title='Insufficient Permissions! :no_entry_sign:',
            description='You lack the power to invoke lockdown! :no_entry_sign:',
            color=discord.Color.purple()
        )
        await ctx.send(embed=embed)

@bot.command(name='unlock')
async def unlock(ctx):
    # Check if the user issuing the command is an administrator
    if ctx.message.author.guild_permissions.administrator:
        channel = ctx.channel

        # Enable send message permission for @everyone role
        await channel.set_permissions(ctx.guild.default_role, send_messages=True)

        # Unique response with embed
        embed = discord.Embed(
            title='Unlock Initiated! :unlock:',
            description='This channel has been unsealed. Messages can flow once again! :partying_face:',
            color=discord.Color.dark_purple()
        )
        await ctx.send(embed=embed)
    else:
        # Unique response with embed
        embed = discord.Embed(
            title='Insufficient Permissions! :no_entry_sign:',
            description='You lack the power to lift the lockdown! :no_entry_sign:',
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

# Create a Flask web server
app = Flask(__name__)

# Define a route for the homepage
@app.route('/')
def home():
    return 'Hello, this is your Discord bot page!'

# Start the Flask web server in a separate thread
from threading import Thread

def run_flask():
    app.run(port=5000)

flask_thread = Thread(target=run_flask)
flask_thread.start()

@bot.command(name='panel', pass_context=True)
async def create_panel(ctx, *, title_and_description):
    global ticket_count
    if ctx.message.author.guild_permissions.administrator:
        channel = ctx.message.channel

        separator = ' | '
        if separator in title_and_description:
            title, description = title_and_description.split(separator, 1)
        else:
            title = title_and_description
            description = ""

        embed = discord.Embed(title=title, description=description, color=DEFAULT_COLOR)

        # Add the "Create Ticket" reaction to the embed
        message = await channel.send(embed=embed)
        await message.add_reaction('🎫')

@bot.event
async def on_raw_reaction_add(payload):
    global ticket_count
    # Check if the reaction is added to a message in a guild
    if payload.guild_id is None:
        return

    guild_id = str(payload.guild_id)
    user = bot.get_user(payload.user_id)

    # Check if the user is not a bot
    if not user.bot:
        guild = bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)

        # Check if the emoji is "🛑"
        if payload.emoji.name == '🛑':
            # Get the ticket channel and check if the user is the creator or a moderator
            ticket_channel = bot.get_channel(payload.channel_id)
            creator_id = int(ticket_channel.name.split('-')[-1])
            creator = guild.get_member(creator_id)

            if user == creator or (member and member.guild_permissions.administrator):
                # Close the ticket by deleting the channel
                await ticket_channel.delete()
            else:
                # Remove the user's reaction if they don't have permission to close the ticket
                message = await ticket_channel.fetch_message(payload.message_id)
                await message.remove_reaction(payload.emoji, user)
        elif payload.emoji.name == '🎫':
            # Check if the user is not a bot
            if not user.bot:
                # Fetch the ticket count for the server from the database
                cursor.execute('''SELECT count FROM ticket_counts WHERE server_id=?''', (guild_id,))
                result = cursor.fetchone()

                if result:
                    ticket_count = result[0]
                else:
                    ticket_count = 0

                # Increment the ticket count
                ticket_count += 1

                # Format the ticket number with leading zeros (e.g., 001, 002)
                ticket_number = f"{ticket_count:03d}"

                # Update the ticket count in the database
                cursor.execute('''INSERT OR REPLACE INTO ticket_counts (server_id, count) VALUES (?, ?)''', (guild_id, ticket_count))
                conn.commit()

                # Create a new ticket channel
                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    member: discord.PermissionOverwrite(read_messages=True, send_messages=True)
                }

                ticket_channel = await guild.create_text_channel(name=f'ticket-{ticket_number}', overwrites=overwrites)

                # Send a welcome message in the ticket channel
                welcome_message = f"Welcome to your ticket, {member.mention}! Feel free to ask for assistance here."
                close_message = "To close this ticket, react with 🛑."

                ticket_message = await ticket_channel.send(f"{welcome_message}\n\n{close_message}")

                # Add the "Close Ticket" reaction to the ticket message
                await ticket_message.add_reaction('🛑')

# Modify the spawn_pokemon_task to set the level of spawned Pokemon to 5
@tasks.loop(minutes=2)
async def spawn_pokemon_task():
    for guild in bot.guilds:
        for channel_id in get_enabled_channels(guild.id):
            channel = bot.get_channel(channel_id)
            if channel:
                # Spawn Pokemon with level 5
                pokemon_name = get_random_pokemon()
                spawn_level = 5

                embed = discord.Embed(title=f"Who's That Pokemon? (Level {spawn_level})", color=discord.Color.dark_purple())
                embed.set_image(url=get_pokemon_image(pokemon_name))
                await channel.send(embed=embed)

                # Update last spawn time, last spawned Pokemon, and its level
                cursor.execute('UPDATE pokemon_spawn SET last_spawn_time = ?, last_spawned_pokemon = ?, last_spawned_level = ? WHERE server_id = ? AND channel_id = ?', (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), pokemon_name, spawn_level, guild.id, channel_id))
                conn.commit()

# Modify the spawn_pokemon function
async def spawn_pokemon(server_id, channel_id):
    global spawn_task_running
    spawn_task_running = True

    channel = bot.get_channel(channel_id)
    if channel:
        # Spawn Pokemon
        pokemon_name = get_random_pokemon()
        embed = discord.Embed(title=f"Who's That Pokemon?", color=discord.Color.dark_purple())
        embed.set_image(url=get_pokemon_image(pokemon_name))
        await channel.send(embed=embed)

        # Send the additional message
        await channel.send(f"This is {pokemon_name}")

        # Update last spawned Pokemon and user for this channel
        last_spawned_pokemon_dict[channel_id] = {'pokemon': pokemon_name, 'user': None}

        # Update last spawn time
        cursor.execute('UPDATE pokemon_spawn SET last_spawn_time = ?, last_spawned_pokemon = ? WHERE server_id = ? AND channel_id = ?', (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), pokemon_name, server_id, channel_id))
        conn.commit()

    spawn_task_running = False
@bot.command(name='pokemon')
@commands.has_permissions(manage_messages=True)
async def enable_pokemon_spawn(ctx):
    server_id = ctx.guild.id
    channel_id = ctx.channel.id

    # Check if already enabled
    cursor.execute('SELECT spawn_enabled FROM pokemon_spawn WHERE server_id = ? AND channel_id = ?', (server_id, channel_id))
    result = cursor.fetchone()

    if result and result[0] == 1:
        await ctx.send('Pokemon spawn is already enabled in this channel.')
    else:
        # Enable Pokemon spawn
        cursor.execute('INSERT OR REPLACE INTO pokemon_spawn VALUES (?, ?, ?, ?, ?, ?, ?)', (server_id, channel_id, 1, 120, '1970-01-01 00:00:00', '', 5))
        conn.commit()
        await ctx.send('Pokemon spawn enabled in this channel. Pokemon will spawn every 2 minutes.')

def get_enabled_channels(server_id):
    cursor.execute('SELECT channel_id FROM pokemon_spawn WHERE server_id = ? AND spawn_enabled = 1', (server_id,))
    return [row[0] for row in cursor.fetchall()]

def get_last_spawn_time(server_id, channel_id):
    cursor.execute('SELECT last_spawn_time FROM pokemon_spawn WHERE server_id = ? AND channel_id = ?', (server_id, channel_id))
    result = cursor.fetchone()
    return result[0] if result else None

def get_cooldown_seconds(server_id, channel_id):
    cursor.execute('SELECT cooldown_seconds FROM pokemon_spawn WHERE server_id = ? AND channel_id = ?', (server_id, channel_id))
    result = cursor.fetchone()
    return result[0] if result else None

# Function to get a random Pokemon name
def get_random_pokemon():
    response = requests.get(pokemon_list_url)

    if response.status_code == 200:
        pokemon_data = response.json()
        return random.choice(pokemon_data)
    else:
        return 'MissingNo'  # Default value if the request fails

def get_pokemon_image(pokemon_name):
    api_url = f'https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower()}/'
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        sprite_url = data['sprites']['front_default']
        # Skip image processing for now
        return sprite_url
    else:
        return f'https://example.com/default_pokemon_image.png'

@bot.command(name='prefix')
@commands.has_permissions(manage_guild=True)
async def set_prefix(ctx, new_prefix: str):
    guild_id = str(ctx.guild.id)

    # Update the bot's command prefix dynamically
    bot.command_prefix = new_prefix

    # Update the database with the new prefix
    cursor.execute('INSERT OR REPLACE INTO server_prefixes VALUES (?, ?, ?)', (guild_id, bot.command_prefix, new_prefix))
    conn.commit()

    # Inform the user about the prefix change
    await ctx.send(f'Prefix updated! New prefix: `{new_prefix}`')
# Your other commands and bot setup...

bot.add_command(purge_messages)
bot.add_command(daily)
bot.add_command(check_balance)
bot.add_command(coinflip)
bot.add_command(pay)
bot.add_command(leaderboard)
bot.add_command(add_role) 
bot.add_command(del_role)
bot.add_command(assign_role)
bot.add_command(tenor_search)
bot.add_command(giphy)
bot.add_command(Neocustom_help)
bot.add_command(issue_warning)
bot.add_command(color_code)
bot.add_command(set_slowmode)
bot.add_command(disable_slowmode)
bot.add_command(server_info)
bot.add_command(member_count)
bot.add_command(server_icon)
bot.add_command(user_avatar)
bot.add_command(rename_channel)
bot.add_command(add_neo)
bot.add_command(create_channel)
bot.add_command(delete_channel)
bot.add_command(slots)
bot.add_command(bank_deposit)
bot.add_command(bank_withdraw)
bot.add_command(bank_balance)
#Close the database connection when the bot is stopped
bot.run(TOKEN)
conn.close()
