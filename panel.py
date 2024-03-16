import discord
from discord.ext import commands
import sqlite3

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='Neo ', intents=intents)

# Set a default color for the embed
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
    print(f'{bot.user.name} has connected to Discord!')

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
