import asyncio
import urllib
import requests
import re
import random
import json
import base64
import binascii
import collections
import string
import sys
import os
import urllib.parse
from urllib.request import urlopen
import io
from dateutil.parser import parse
import time
import datetime
from datetime import timezone
from datetime import datetime
import discord
from discord.ext.commands import Bot
from discord.ext import commands
from colorthief import ColorThief
from help_info import *
from auth import *
client = discord.Client()
bot = commands.Bot(command_prefix='>')
extensions = ['encoding_decoding', 'cipher', 'ctfs', 'utility']
bot.remove_command('help')
blacklisted = []
cool_names = ['nullpxl', 'Test_Monkey', 'Yiggles', 'JohnHammond'] # This is intended to be able to be circumvented.
# If you do something like report a bug with the report command (OR GITHUB), e.g, >report "a bug", you might be added to the list!

@bot.event
async def on_ready():
    print(('<' + bot.user.name) + ' Online>')
    print(discord.__version__)
    await bot.change_presence(activity=discord.Game(name='>help | in development'))

@bot.event
async def on_message(message):
    if 'who should I subscribe to?' in message.content:
        choice = random.randint(1, 2)
        
        if choice == 1:
            await message.channel.send('https://youtube.com/nullpxl')
        
        if choice == 2:
            await message.channel.send('https://www.youtube.com/user/RootOfTheNull')
    
    await bot.process_commands(message)

# Sends the github link.
@bot.command()
async def source(ctx):
    await ctx.send(src)

@bot.command()
async def help(ctx, page=None):
    if (not page) or (page == '1'):
        page_num = '1'
        emb = discord.Embed(description=help_page, colour=4387968)
        emb.set_author(name='>request "x" - request a feature')
    
    if page == '2':
        emb = discord.Embed(description=help_page_2, colour=4387968)
        emb.set_author(name='>request "x" - request a feature')
    
    await ctx.channel.send(embed=emb)

# Bot sends a dm to creator with the name of the user and their request.
@bot.command()
async def request(ctx, feature):
    creator = await bot.get_user_info(230827776637272064)
    authors_name = str(ctx.author)
    await creator.send(f''':pencil: {authors_name}: {feature}''')
    await ctx.send(f''':pencil: Thanks, "{feature}" has been requested!''')

# Bot sends a dm to creator with the name of the user and their report.
@bot.command()
async def report(ctx, error_report):
    creator = await bot.get_user_info(230827776637272064)
    authors_name = str(ctx.author)
    await creator.send(f''':triangular_flag_on_post: {authors_name}: {error_report}''')
    await ctx.send(f''':triangular_flag_on_post: Thanks for the help, "{error_report}" has been reported!''')

@bot.command()
async def creator(ctx):
    await ctx.send(creator_info)

@bot.command()
async def amicool(ctx):
    authors_name = str(ctx.author)
    
    if any((name in authors_name for name in cool_names)):
        await ctx.send('You are very cool')
    else:
        await ctx.send('lolno')

if __name__ == '__main__':
    sys.path.insert(1, os.getcwd() + '/cogs/')
    for extension in extensions:
        bot.load_extension(extension)
    bot.run(auth_token)