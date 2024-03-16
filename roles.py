import discord
from discord.ext import commands

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='Neo ', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command(name='addrole', pass_context=True)
async def add_role(ctx, name, color, hoist):
    # Check if the user has administrator permissions
    if ctx.message.author.guild_permissions.administrator:
        # Create a role with specified name, color, and hoist
        role = await ctx.guild.create_role(name=name, color=discord.Colour(int(color[1:], 16)), hoist=bool(hoist))

        # Create an embed message with red color
        embed = discord.Embed(title="Role Added", description=f"Role '{name}' created with color #{color} and hoist set to {hoist}.", color=discord.Colour.dark_purple())

        # Send the embed message
        await ctx.send(embed=embed)
    else:
        # Send a message if the user doesn't have administrator permissions
        await ctx.send("You don't have the necessary permissions to use this command.")

@bot.command(name='delrole', pass_context=True)
async def del_role(ctx, name):
    # Check if the user has administrator permissions
    if ctx.message.author.guild_permissions.administrator:
        # Find the role by name
        role = discord.utils.get(ctx.guild.roles, name=name)

        # Check if the role exists
        if role:
            # Delete the role
            await role.delete()

            # Send a confirmation message
            await ctx.send(f"Role '{name}' deleted successfully.")
        else:
            # Send a message if the role doesn't exist
            await ctx.send(f"Role '{name}' not found.")
    else:
        # Send a message if the user doesn't have administrator permissions
        await ctx.send("You don't have the necessary permissions to use this command.")

@bot.command(name='role', pass_context=True)
async def assign_role(ctx, user: discord.Member, role_name):
    # Check if the user has administrator permissions
    if ctx.message.author.guild_permissions.administrator:
        # Find the role by name
        role = discord.utils.get(ctx.guild.roles, name=role_name)

        # Check if the role exists
        if role:
            # Assign the role to the specified user
            await user.add_roles(role)

            # Send a confirmation message
            await ctx.send(f"Role '{role_name}' assigned to {user.mention} successfully.")
        else:
            # Send a message if the role doesn't exist
            await ctx.send(f"Role '{role_name}' not found.")
    else:
        # Send a message if the user doesn't have administrator permissions
        await ctx.send("You don't have the necessary permissions to use this command.")
