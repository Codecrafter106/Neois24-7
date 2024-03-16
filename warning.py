import discord
from discord.ext import commands
import sqlite3

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='Neo ', intents=intents)

# Connect to SQLite database
conn = sqlite3.connect('warnings.db')
cursor = conn.cursor()

# Create the table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS warnings (
        guild_id TEXT,
        user_id TEXT,
        warnings INTEGER,
        PRIMARY KEY (guild_id, user_id)
    )
''')
conn.commit()

@bot.command(name='warning')
@commands.has_permissions(manage_messages=True)  # Check if the user has 'manage_messages' permission
async def issue_warning(ctx, user: discord.User, *, reason):
    guild_id = str(ctx.guild.id)
    user_id = str(user.id)

    # Insert or update the user's warning count in the database
    cursor.execute('INSERT OR REPLACE INTO warnings VALUES (?, ?, COALESCE((SELECT warnings FROM warnings WHERE guild_id = ? AND user_id = ?) + 1, 1))', (guild_id, user_id, guild_id, user_id))
    conn.commit()

    # Fetch the updated warning count for the user
    cursor.execute('SELECT warnings FROM warnings WHERE guild_id = ? AND user_id = ?', (guild_id, user_id))
    warnings = cursor.fetchone()[0]

    # Create an embed to display the warning message
    embed = discord.Embed(
        title=f'Warning - {user.name}',
        description=f'Reason: {reason}\nWarnings: {warnings}',
        color=discord.Color.dark_purple()
    )
    embed.set_thumbnail(url=user.avatar)

    # Send the warning message in the same channel
    await ctx.send(embed=embed)

# Your other commands and bot setup...
