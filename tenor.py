import os
import discord
from discord.ext import commands
import requests
import json
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='Neo ', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command(name='tenor', pass_context=True)
async def tenor_search(ctx, *search_terms):
    # Combine search terms into a single string
    search_query = ' '.join(search_terms)

    # Set up the Tenor API endpoint and parameters
    api_key = 'LIVDSRZULELA'  # Replace with your Tenor API key
    api_url = f'https://api.tenor.com/v1/search?q={search_query}&key={api_key}&limit=1'

    try:
        # Make a request to the Tenor API
        response = requests.get(api_url)
        data = response.json()

        # Extract the GIF URL from the API response
        gif_url = data['results'][0]['media'][0]['gif']['url']

        # Send the GIF in an embed message
        embed = discord.Embed(title=f'Tenor Search: {search_query}', color=discord.Colour.dark_purple())
        embed.set_image(url=gif_url)

        await ctx.send(embed=embed)

    except Exception as e:
        print(f'Error during Tenor search: {e}')
        await ctx.send('Error during Tenor search. Please try again later.')

@bot.command(name='giphy', help='Search animated GIFs from Giphy.')
async def giphy(ctx, *search_terms):
    search_query = ' '.join(search_terms)

    # Giphy API key (replace 'YOUR_GIPHY_API_KEY' with your actual API key)
    api_key = 'rrUAHTEvX0edrEgKA7ZcogVwyADu7bjs'

    # Giphy API endpoint for searching GIFs
    api_endpoint = 'https://api.giphy.com/v1/gifs/search'

    # Set up parameters for the Giphy API request
    params = {
        'api_key': api_key,
        'q': search_query,
        'limit': 5  # You can adjust the limit as needed
    }

    # Make a request to the Giphy API
    response = requests.get(api_endpoint, params=params)
    data = json.loads(response.text)

    # Check if the response contains any GIFs
    if 'data' in data and data['data']:
        # Display the first GIF as the primary result
        primary_gif_url = data['data'][0]['images']['original']['url']
        await ctx.send(f'**GIF Search Result:**\n{primary_gif_url}')

        # Display other GIFs as alternatives
        for gif_data in data['data'][1:]:
            gif_url = gif_data['images']['original']['url']
            await ctx.send(gif_url)
    else:
        await ctx.send('No GIFs found for the given search terms.')
