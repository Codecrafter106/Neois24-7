import asyncio
import discord
from discord.ext import commands
import sqlite3
import random
import datetime
from typing import Union

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='Neo ', intents=intents)

# Connect to SQLite database
conn = sqlite3.connect('user_data.db')
cursor = conn.cursor()

# Create table to store user balance and cooldown information
cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_data (
        user_id INTEGER PRIMARY KEY,
        balance INTEGER DEFAULT 0,
        daily_cooldown TIMESTAMP DEFAULT NULL
    )
''')

# Create table to store bank balance information
cursor.execute('''
    CREATE TABLE IF NOT EXISTS bank_data (
        user_id INTEGER PRIMARY KEY,
        balance INTEGER DEFAULT 0
    )
''')

conn.commit()


# Define daily cooldown duration (24 hours)
DAILY_COOLDOWN = commands.CooldownMapping.from_cooldown(1, 24 * 60 * 60, commands.BucketType.user)
Neocommand_info = {'Balance': {'trigger': '•Neo bal,Neo balance', 'title': 'Neo balance command'},
'Daily': {'trigger': '•Neo daily', 'title': 'Get daily Neo reward'}, 
'Coinflip': {'trigger': '•Neo coinflip,Neo cf', 'title': 'Place your bet on coinflip'},
'Pay': {'trigger': '•Neo pay', 'title': 'Send your Neo to others'}, 
'Leaderboard': {'trigger': '•Neo leaderboard', 'title': 'check top Neo balance user '},
'Slots': {'trigger': '•Neo slots', 'title': 'Play the slot machine'},
'Bank_Balance': {'trigger': '•Neo bankbalance', 'title': 'Check your bank balance'},
'Bank_deposit': {'trigger': '•Neo bankdeposit', 'title': 'Deposit your Neo to bank'}, 
'Bank_withdraw': {'trigger': '•Neo bankwithdraw', 'title': 'Withdraw your Neo from bank'},
                  }                             
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command(name='nhelp')
async def Neocustom_help(ctx):
    author = ctx.author
    commands_per_page = 10

    def generate_help_embed():
        embed = discord.Embed(title=f'NeoHelp - Page 1', color=0x800080)

        for trigger, info in Neocommand_info.items():
            embed.add_field(name=f'{info["trigger"]}', value=f'{info["title"]}', inline=False)

        embed.set_footer(text='More Neo commands will be added in the future.')
        return embed

    Neohelp_embed = generate_help_embed()
    await ctx.send(embed=Neohelp_embed)

@bot.command(name='balance', aliases=['bal', 'BaL', 'BAL', 'Balance', 'BALANCE', 'b'])
async def check_balance(ctx):
    user_id = ctx.author.id
    cursor.execute('SELECT balance FROM user_data WHERE user_id = ?', (user_id,))
    user_balance = cursor.fetchone()

    if user_balance is None:
        cursor.execute('INSERT INTO user_data (user_id, balance) VALUES (?, 0)', (user_id,))
        conn.commit()
        user_balance = (0,)

    formatted_balance = '{:,}'.format(user_balance[0])  # Adding commas for better readability

    balance_message = f'**{ctx.author.mention}**, you currently have **{formatted_balance}** Neo'

    if user_balance[0] == 0:
        balance_message += " 💸"
    elif user_balance[0] < 100:
        balance_message += " 🪙"
    elif user_balance[0] < 500:
        balance_message += " 🌟"
    else:
        balance_message += " 💰"

    await ctx.send(balance_message)


@bot.command(name='daily', aliases=['dy', 'DY', 'Daily', 'DAILY','DailY'])
async def daily(ctx):
    user_id = ctx.author.id

    # Check if user is on daily cooldown
    cursor.execute('SELECT daily_cooldown FROM user_data WHERE user_id = ?', (user_id,))
    last_daily_cooldown = cursor.fetchone()

    # Get the current time outside the if block
    current_time = datetime.datetime.utcnow()

    if last_daily_cooldown is not None and last_daily_cooldown[0] is not None:
        last_daily_cooldown = datetime.datetime.fromisoformat(last_daily_cooldown[0])
        remaining_time = (last_daily_cooldown + datetime.timedelta(days=1)) - current_time

        if remaining_time.total_seconds() > 0:
            # Display remaining time in hours or minutes
            hours, remainder = divmod(int(remaining_time.total_seconds()), 3600)
            minutes = remainder // 60

            if hours > 0:
                await ctx.send(f"{ctx.author.mention}, you're on daily cooldown. Please wait **{hours}** hours.")
            else:
                await ctx.send(f"{ctx.author.mention}, you're on daily cooldown. Please wait **{minutes}** minutes.")
            return

    # Generate random UwU amount between 500 and 1500
    Neo_amount = random.randint(500, 1500)

    # Update user balance and daily_cooldown timestamp
    cursor.execute('''
        INSERT OR REPLACE INTO user_data (user_id, balance, daily_cooldown) 
        VALUES (?, COALESCE((SELECT balance FROM user_data WHERE user_id = ?), 0) + ?, ?)
    ''', (user_id, user_id, Neo_amount, current_time))
    conn.commit()

    # Display output with emojis
    if Neo_amount == 0:
        await ctx.send(f"{ctx.author.mention}, you didn't earn any Neo today. 💸")
    elif Neo_amount < 100:
        await ctx.send(f"**{ctx.author.mention}**, you earned **{Neo_amount}** Neo today! 🪙")
    elif Neo_amount < 500:
        await ctx.send(f"**{ctx.author.mention}**, you earned **{Neo_amount}** Neo today! 🌟")
    else:
        await ctx.send(f"**{ctx.author.mention}**, you hit the jackpot! You earned **{Neo_amount}** Neo today! 💰")

@bot.command(name='cf', aliases=['coinflip', 'CF', 'Coinflip', 'COINFLIP', 'CoinFlip'])
async def coinflip(ctx, amount: Union[int, str], choice: str = None):
    user_id = ctx.author.id
    cursor.execute('SELECT balance FROM user_data WHERE user_id = ?', (user_id,))
    user_balance = cursor.fetchone()

    if user_balance is None or (isinstance(amount, int) and user_balance[0] < amount):
        await ctx.send(f'{ctx.author.mention}, you don\'t have enough **Neo** to place that bet.')
        return

    if isinstance(amount, str) and amount.lower() == 'all':
        if user_balance[0] == 0:
            await ctx.send(f'{ctx.author.mention}, you cannot use "all" when your balance is **0**.')
            return
        amount = user_balance[0]

    # Apply the limit for the maximum bet amount
    max_bet = 300000
    if amount > max_bet:
        amount = max_bet
        await ctx.send(f'{ctx.author.mention}, the maximum bet amount is **{max_bet} Neo**. Your bet has been limited to this amount.')

    if choice is None:
        # If user didn't explicitly choose heads or tails, bot chooses heads
        choice = 'heads'

    normalized_choice = choice.lower()

    # Define aliases for heads and tails
    heads_aliases = ['heads', 'h']
    tails_aliases = ['tails', 't']

    if normalized_choice not in heads_aliases + tails_aliases:
        await ctx.send(f'{ctx.author.mention}, please choose either **heads** or **tails** for the coinflip.')
        return

    result = random.choice(['heads', 'tails'])

    cursor.execute('UPDATE user_data SET balance = balance - ? WHERE user_id = ?', (amount, user_id))
    conn.commit()

    # Send initial message
    coinflip_message = await ctx.send(f'**{ctx.author.mention}**, you spent 💰**{amount:,}** **Neo** and choose **{normalized_choice}** '
                                      f'your coinflip is in progress... :coin:')

    # Wait for 3 seconds
    await asyncio.sleep(3)

    # Edit the initial message with the result and win/lose information
    if (result == 'heads' and normalized_choice in heads_aliases) or \
       (result == 'tails' and normalized_choice in tails_aliases):
        winnings = amount * 2
        cursor.execute('UPDATE user_data SET balance = balance + ? WHERE user_id = ?', (winnings, user_id))
        conn.commit()
        await coinflip_message.edit(content=f'**{ctx.author.mention}**, you spent 💰**{amount:,}** **Neo** and choose **{normalized_choice}** '
                                            f'The coin :coin: landed on **{result}**. You won 💰**{winnings:,}** **Neo**!')
    else:
        await coinflip_message.edit(content=f'**{ctx.author.mention}**, you spent 💰**{amount:,}** **Neo** and choose **{normalized_choice}** '
                                            f'The coin :coin: landed on **{result}**. You lost 💰**{amount:,}** **Neo**.')
         
@bot.command(name='pay', aliases=['send', 'transfer', 'p', 'P'])
async def pay(ctx, recipient: discord.User, amount: Union[int, str]):
    user_id = ctx.author.id

    if recipient.id == user_id:
        await ctx.send(f'{ctx.author.mention}, you cannot send Neo to yourself.')
        return

    if isinstance(amount, str) and amount.lower() == 'all':
        amount = cursor.execute('SELECT balance FROM user_data WHERE user_id = ?', (user_id,)).fetchone()[0]

    amount = int(amount)

    if amount <= 0:
        await ctx.send(f'{ctx.author.mention}, please enter an amount greater than 0 for the payment.')
        return

    cursor.execute('SELECT balance FROM user_data WHERE user_id = ?', (user_id,))
    user_balance = cursor.fetchone()

    if user_balance is None or user_balance[0] < amount:
        await ctx.send(f'{ctx.author.mention}, you don\'t have enough Neo to make that payment.')
        return

    cursor.execute('UPDATE user_data SET balance = balance - ? WHERE user_id = ?', (amount, user_id))
    cursor.execute('INSERT OR IGNORE INTO user_data (user_id, balance) VALUES (?, 0)', (recipient.id,))
    cursor.execute('UPDATE user_data SET balance = balance + ? WHERE user_id = ?', (amount, recipient.id))
    conn.commit()

    await ctx.send(f'**{ctx.author.mention}**, **{amount:,}** Neo successfully sent to **{recipient.mention}!**')

@bot.command(name='add')
async def add_neo(ctx, amount: int):
    YOUR_USER_ID = 1055555345591844945  # Replace this with your actual user ID
    if ctx.author.id != YOUR_USER_ID:
        await ctx.send("This command is restricted to the bot owner.")
        return
    
    cursor.execute('SELECT balance FROM user_data WHERE user_id = ?', (YOUR_USER_ID,))
    user_balance = cursor.fetchone()
    if user_balance is None:
        cursor.execute('INSERT INTO user_data (user_id, balance, daily_cooldown) VALUES (?, ?, NULL)', (YOUR_USER_ID, amount))
    else:
        new_balance = user_balance[0] + amount
        cursor.execute('UPDATE user_data SET balance = ? WHERE user_id = ?', (new_balance, YOUR_USER_ID))
    conn.commit()
    await ctx.send(f'**{amount} Neo successfully added to your balance!**')

@bot.command(name='leaderboard', aliases=['lb', 'Leaderboard', 'LB', 'LeaderBoard'])
async def leaderboard(ctx):
    cursor.execute('SELECT user_id, balance FROM user_data ORDER BY balance DESC')
    top_users = cursor.fetchall()

    # Filter users who are currently in the server
    server_members = [member.id for member in ctx.guild.members]
    top_users = [(user_id, balance) for user_id, balance in top_users if user_id in server_members]

    leaderboard_text = generate_leaderboard_text(ctx, top_users)
    await ctx.send(leaderboard_text)


def generate_leaderboard_text(ctx, top_users):
    server_name = ctx.guild.name
    user_id = ctx.author.id
    user_rank = None

    text = f"```css\nTop {len(top_users)} Ranking for {server_name}:\n\n"

    for rank, (user_id, balance) in enumerate(top_users, start=1):
        user_name = ctx.guild.get_member(user_id).name
        formatted_balance = '{:,}'.format(balance)
        text += f"#{rank} {user_name}: {formatted_balance} Neo\n"

        if user_id == ctx.author.id:
            user_rank = rank

    text += f"\nYou rank - {user_rank}\n```"
    return text


@bot.command(name='slots', aliases=['s', 'S', 'Slots', 'Slot', 'slot', 'SLOTS', 'SLOT'])
async def slots(ctx, amount: int):
    user_id = ctx.author.id

    # Check if user has enough balance
    cursor.execute('SELECT balance FROM user_data WHERE user_id = ?', (user_id,))
    user_balance = cursor.fetchone()

    if user_balance is None or user_balance[0] < amount:
        await ctx.send(f'{ctx.author.mention}, you don\'t have enough **Neo** to play slots.')
        return

    # Deduct the betting amount from user's balance
    cursor.execute('UPDATE user_data SET balance = balance - ? WHERE user_id = ?', (amount, user_id))
    conn.commit()

    # Define emojis for slots
    emojis = ['🍆', '❤', '🌹', '💰']

    # Generate random slots result
    slots_result = [random.choice(emojis) for _ in range(3)]

    # Display initial message with first slot emoji
    slot_message = await ctx.send(f'**{ctx.author.mention}**,You bet **{amount:,} Neo**,Your slot machine is spinning... ```{slots_result[0]} ?? ??```')

    # Wait for 2 seconds before revealing second slot emoji
    await asyncio.sleep(2)
    await slot_message.edit(content=f'**{ctx.author.mention}**,You bet **{amount:,} Neo**, Your slot machine is spinning... ```{slots_result[0]} {slots_result[1]} ??```')

    # Wait for another 2 seconds before revealing third slot emoji
    await asyncio.sleep(2)
    await slot_message.edit(content=f'**{ctx.author.mention}**, You bet **{amount:,} Neo**, Your slot machine is spinning... ```{slots_result[0]} {slots_result[1]} {slots_result[2]}```')

    # Calculate winnings based on slots result
    if slots_result.count(slots_result[0]) == 3:
        if slots_result[0] == '🍆':
            winnings = amount
        elif slots_result[0] == '❤':
            winnings = amount * 2
        elif slots_result[0] == '🌹':
            winnings = amount * 3
        elif slots_result[0] == '💰':
            winnings = amount * 5
    else:
        winnings = 0

    # Add winnings to user's balance
    cursor.execute('UPDATE user_data SET balance = balance + ? WHERE user_id = ?', (winnings, user_id))
    conn.commit()

    # Display outcome of slots game
    if winnings > 0:
        await slot_message.edit(content=f'**{ctx.author.mention}**,Your bet **{amount:,} Neo**, Slot machine stopped at ```{" | ".join(slots_result)}```! '
                                         f'You won 💰**{winnings}** Neo!')
    else:
        await slot_message.edit(content=f'**{ctx.author.mention}**, You bet **{amount:,} Neo**, Slot machine stopped at ```{" | ".join(slots_result)}```! '
                                         f'Better luck next time!')
@bot.command(name='bankdeposit', aliases=['deposit', 'd', 'D', 'DEPOSIT'])
async def bank_deposit(ctx, amount: Union[int, str]):
    user_id = ctx.author.id

    if isinstance(amount, str) and amount.lower() == 'all':
        # Check the user's current balance
        cursor.execute('SELECT balance FROM user_data WHERE user_id = ?', (user_id,))
        user_balance = cursor.fetchone()

        if user_balance is None or user_balance[0] <= 0:
            await ctx.send(f'{ctx.author.mention}, you don\'t have any Neo to deposit.')
            return

        # Deduct the deposit amount from user's balance
        deposit_amount = user_balance[0]
        cursor.execute('UPDATE user_data SET balance = 0 WHERE user_id = ?', (user_id,))
        conn.commit()

        # Add the deposit amount to user's bank balance
        cursor.execute('INSERT OR IGNORE INTO bank_data (user_id, balance) VALUES (?, 0)', (user_id,))
        cursor.execute('UPDATE bank_data SET balance = balance + ? WHERE user_id = ?', (deposit_amount, user_id))
        conn.commit()

        # Get current user's name
        user_name = ctx.author.name

        # Get current date and time
        deposit_dateandtime = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        # Prepare the embed message
        embed = discord.Embed(title='Neo Official Bank', description=f'**{user_name} bank account\n**You deposit {deposit_amount:,} Neo', color=discord.Color.dark_purple())
        embed.add_field(name='Date & Time', value=deposit_dateandtime)

        await ctx.send(embed=embed)

    elif isinstance(amount, int):
        # Check if user has enough balance to deposit
        cursor.execute('SELECT balance FROM user_data WHERE user_id = ?', (user_id,))
        user_balance = cursor.fetchone()

        if user_balance is None or user_balance[0] < amount:
            await ctx.send(f'{ctx.author.mention}, you don\'t have enough Neo to deposit that amount.')
            return

        # Deduct the deposit amount from user's balance
        cursor.execute('UPDATE user_data SET balance = balance - ? WHERE user_id = ?', (amount, user_id))
        conn.commit()

        # Add the deposit amount to user's bank balance
        cursor.execute('INSERT OR IGNORE INTO bank_data (user_id, balance) VALUES (?, 0)', (user_id,))
        cursor.execute('UPDATE bank_data SET balance = balance + ? WHERE user_id = ?', (amount, user_id))
        conn.commit()

        # Get current user's name
        user_name = ctx.author.name

        # Get current date and time
        deposit_dateandtime = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        # Prepare the embed message
        embed = discord.Embed(title='Neo Official Bank', description=f'**{user_name} bank account\n**You deposit {amount:,} Neo', color=discord.Color.dark_purple())
        embed.add_field(name='Date & Time', value=deposit_dateandtime)

        await ctx.send(embed=embed)

    else:
        await ctx.send(f'{ctx.author.mention}, please provide a valid amount to deposit.')

@bot.command(name='bankwithdraw', aliases=['withdraw', 'W', 'w', 'WITHDRAW'])
async def bank_withdraw(ctx, amount: Union[int, str]):
    user_id = ctx.author.id

    if isinstance(amount, str) and amount.lower() == 'all':
        # Check the user's current bank balance
        cursor.execute('SELECT balance FROM bank_data WHERE user_id = ?', (user_id,))
        bank_balance = cursor.fetchone()

        if bank_balance is None or bank_balance[0] <= 0:
            await ctx.send(f'{ctx.author.mention}, you don\'t have any Neo in your bank to withdraw.')
            return

        # Withdraw the entire bank balance
        withdraw_amount = bank_balance[0]
        cursor.execute('UPDATE bank_data SET balance = 0 WHERE user_id = ?', (user_id,))
        conn.commit()

        # Add the withdrawn amount to user's balance
        cursor.execute('UPDATE user_data SET balance = balance + ? WHERE user_id = ?', (withdraw_amount, user_id))
        conn.commit()

        # Get current user's name
        user_name = ctx.author.name

        # Get current date and time
        withdraw_dateandtime = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        # Prepare the embed message
        embed = discord.Embed(title='Neo Official Bank', description=f'**{user_name} Neo Bank account\n**You withdrew {withdraw_amount:,} Neo', color=discord.Color.dark_purple())
        embed.add_field(name='Before Withdraw Bank balance', value=f'{bank_balance[0]:,} Neo', inline=False)
        embed.add_field(name='Current Bank balance', value='0 Neo', inline=False)
        embed.add_field(name='Date & Time', value=withdraw_dateandtime)

        await ctx.send(embed=embed)

    elif isinstance(amount, int):
        # Check if user has enough balance to withdraw
        cursor.execute('SELECT balance FROM bank_data WHERE user_id = ?', (user_id,))
        bank_balance = cursor.fetchone()

        if bank_balance is None or bank_balance[0] < amount:
            await ctx.send(f'{ctx.author.mention}, you don\'t have enough Neo in your bank to withdraw that amount.')
            return

        # Deduct the withdraw amount from user's bank balance
        cursor.execute('UPDATE bank_data SET balance = balance - ? WHERE user_id = ?', (amount, user_id))
        conn.commit()

        # Add the withdraw amount to user's balance
        cursor.execute('UPDATE user_data SET balance = balance + ? WHERE user_id = ?', (amount, user_id))
        conn.commit()

        # Get current user's name
        user_name = ctx.author.name

        # Get current date and time
        withdraw_dateandtime = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        # Prepare the embed message
        embed = discord.Embed(title='Neo Official Bank', description=f'**{user_name} Neo Bank account\n**You withdrauw {amount:,} Neo', color=discord.Color.dark_purple())
        embed.add_field(name='Before Withdraw Bank balance', value=f'{bank_balance[0]:,} Neo', inline=False)
        embed.add_field(name='Current Bank balance', value=f'{bank_balance[0] - amount:,} Neo', inline=False)
        embed.add_field(name='Date & Time', value=withdraw_dateandtime)

        await ctx.send(embed=embed)

    else:
        await ctx.send(f'{ctx.author.mention}, please provide a valid amount to withdraw.')
@bot.command(name='bankbalance', aliases=['bb', 'BB'])
async def bank_balance(ctx):
    user_id = ctx.author.id

    # Fetch user's bank balance
    cursor.execute('SELECT balance FROM bank_data WHERE user_id = ?', (user_id,))
    bank_balance = cursor.fetchone()

    if bank_balance is None:
        await ctx.send(f'{ctx.author.mention}, you don\'t have a Neo bank account yet.')
        return

    # Prepare the embed message
    embed = discord.Embed(title='Neo Official Bank', description=f'**{ctx.author.name} Neo Bank account**', color=discord.Color.dark_purple())
    embed.add_field(name='Current Bank Balance', value=f'{bank_balance[0]:,} Neo')

    await ctx.send(embed=embed)
