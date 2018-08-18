import urllib
import requests
import re
import json
import base64
import binascii
import collections
import string
import urllib.parse
from urllib.request import urlopen
import io
from dateutil.parser import parse
import time
import datetime
from datetime import timezone
from datetime import datetime, timedelta

from colorthief import ColorThief
import discord
from discord.ext import commands

class Ctfs():

    def __init__(self, bot):
        self.bot = bot
        self.challenges = {}
        self.ctfname = ""
    @commands.command()
    async def ctf(self, ctx, cmd, params=None, verbose=None):
        guild = ctx.guild
        category = discord.utils.get(ctx.guild.categories, name="CTF")
        verbose = f"[{verbose}]"
        
        if cmd == 'create':
            if ctx.message.author.id ==  ctx.guild.owner.id or ctx.message.author.id == 230827776637272064:
                await guild.create_text_channel(name=params, category=category)
                await guild.create_role(name=params)
                self.ctfname = params
            else:
                await ctx.send('You must be owner to use this command! Please tag the owner to create the ctf.') 
        
        if cmd == 'challenge':
            
            if params == 'add': # Usage: ctf challenge add challengename
                self.challenges[verbose] = 'Incomplete'
                await ctx.send(':white_check_mark:')
            
            if params == 'solved': # usage: ctf challenge done challengename
                self.challenges[verbose] = str(self.challenges[verbose]).replace('Incomplete', 'Completed!')
                await ctx.send(':triangular_flag_on_post:')
            
            if params == 'list': # Usage: ctf challenge list
                pretty_chal = str(self.challenges).replace(', ', '\n').replace('{', '').replace('}', '').replace("'", '')
                
                try:
                    await ctx.send(f"```ini\n{pretty_chal}```")
                except:
                    await ctx.send("Add a challenge with >ctf challenge add <challengename>")
            
            if params == 'working': # Usage: ctf challenge working challengename
                author = str(ctx.message.author)
                author = re.sub(r'#(\d{4})', '', author)
                self.challenges[verbose] += ' - '+author

                await ctx.send(':white_check_mark:')

        if cmd == 'timeleft': # Return the timeleft in the ctf in days, hours, minutes, seconds
            with open("db.json") as db:
                data = json.load(db)
                running = False
                
                for ctf in data:
                    now = datetime.utcnow()
                    unix_now = int(now.replace(tzinfo=timezone.utc).timestamp())
                    start = datetime.utcfromtimestamp(ctf['start']).strftime('%Y-%m-%d %H:%M:%S') + ' UTC'
                    end = datetime.utcfromtimestamp(ctf['end']).strftime('%Y-%m-%d %H:%M:%S') + ' UTC'
                  
                    if ctf['start'] < unix_now and ctf['end'] > unix_now: #check if ctf is currently running
                        running = True
                        time = ctf['end'] - unix_now 
                        days = time // (24 * 3600)
                        time = time % (24 * 3600)
                        hours = time // 3600
                        time %= 3600
                        minutes = time // 60
                        time %= 60
                        seconds = time
                        await ctx.send(f"```ini\n{ctf['name']} ends in: [{days} days], [{hours} hours], [{minutes} minutes], [{seconds} seconds]```\n{ctf['url']}")
                
                if running == False:
                    await ctx.send('No ctfs are running! Use >ctftime upcoming to see upcoming ctfs')

        if cmd == 'countdown': # Return the time until the ctfs start
            #TODO: find a way to only return the appropriate ctf, if i loop through db.json it'll just spam the user.
            with open("db.json") as db:
                data = json.load(db)
                running = False
                i = 1
                numbers = ""

                if params == None:
                    for ctf in data:
                        numbers += f"\n[{i}] {ctf['name']}\n"
                        i += 1
                    await ctx.send(f"Type >ctf countdown <number> to select.```ini\n{numbers}```")
                else:
                    x = int(params) - 1
                    now = datetime.utcnow()
                    unix_now = int(now.replace(tzinfo=timezone.utc).timestamp())
                    start = datetime.utcfromtimestamp(data[x]['start']).strftime('%Y-%m-%d %H:%M:%S') + ' UTC'
                    end = datetime.utcfromtimestamp(data[x]['end']).strftime('%Y-%m-%d %H:%M:%S') + ' UTC'
                      
                    time = data[x]['start'] - unix_now 
                    days = time // (24 * 3600)
                    time = time % (24 * 3600)
                    hours = time // 3600
                    time %= 3600
                    minutes = time // 60
                    time %= 60
                    seconds = time
                    await ctx.send(f"```ini\n{data[x]['name']} starts in: [{days} days], [{hours} hours], [{minutes} minutes], [{seconds} seconds]```\n{data[x]['url']}")
        
        if cmd == 'join':
            role = discord.utils.get(ctx.guild.roles, name=self.ctfname)
            user = ctx.message.author
            await user.add_roles(role)
            await ctx.send(f"{user} has joined the {self.ctfname} team!")

        if cmd == 'leave':
            role = discord.utils.get(ctx.guild.roles, name=self.ctfname)
            user = ctx.message.author
            await user.remove_roles(role)
            await ctx.send(f"{user} has left the {self.ctfname} team.")

    # Returns upcoming ctfs, leaderboards, and currently running ctfs from ctftime.org (using their api)
    # Usage: ctftime <upcoming/top/current> <number of ctfs/year>
    @commands.command() 
    async def ctftime(self, ctx, status, params=None):
        current_ctftime_cmds = ['upcoming', 'top', 'current']
        default_image = 'https://pbs.twimg.com/profile_images/2189766987/ctftime-logo-avatar_400x400.png'

        def rgb2hex(r, g, b):
            tohex = '#{:02x}{:02x}{:02x}'.format(r, g, b)
            return tohex
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0',
        }
        
        if status == 'upcoming':
            upcoming_url = 'https://ctftime.org/api/v1/events/'
            response = requests.get(upcoming_url, headers=headers, params=params)
            data = response.json()
            
            if params == None:
                params = '3'
            else:
                pass
            
            for num in range(0, int(params)):
                ctf_title = data[num]['title']
                (ctf_start, ctf_end) = (data[num]['start'].replace('T', ' ').split('+', 1)[0] + ' UTC', data[num]['finish'].replace('T', ' ').split('+', 1)[0] + ' UTC')
                (ctf_start, ctf_end) = (re.sub(':00 ', ' ', ctf_start), re.sub(':00 ', ' ', ctf_end))
                dur_dict = data[num]['duration']
                (ctf_hours, ctf_days) = (str(dur_dict['hours']), str(dur_dict['days']))
                ctf_link = data[num]['url']
                ctf_image = data[num]['logo']
                ctf_format = data[num]['format']
                ctf_place = data[num]['onsite']
                
                if ctf_place == False:
                    ctf_place = 'Online'
                else:
                    ctf_place = 'Onsite'
                
                if ctf_image != '':
                    fd = urlopen(ctf_image)
                else:
                    fd = urlopen(default_image)
                
                f = io.BytesIO(fd.read())
                color_thief = ColorThief(f)
                rgb_color = color_thief.get_color(quality=49)
                hexed = str(rgb2hex(rgb_color[0], rgb_color[1], rgb_color[2])).replace('#', '')
                f_color = int(hexed, 16)
                embed = discord.Embed(title=ctf_title, description=ctf_link, color=f_color)
                
                if ctf_image != '':
                    embed.set_thumbnail(url=ctf_image)
                else:
                    embed.set_thumbnail(url=default_image)
                
                embed.add_field(name='Duration', value=((ctf_days + ' days, ') + ctf_hours) + ' hours', inline=True)
                embed.add_field(name='Format', value=(ctf_place + ' ') + ctf_format, inline=True)
                embed.add_field(name='─' * 23, value=(ctf_start + ' -> ') + ctf_end, inline=True)
                await ctx.channel.send(embed=embed)
        
        if status == 'top':
            top_url = 'https://ctftime.org/api/v1/top/'
            response = requests.get(top_url, headers=headers, params=params)
            data = response.json()
            leaderboards = ''
            
            if (not params):
                params = '2018'
            
            for team in range(10):
                rank = team + 1
                teamname = data[params][team]['team_name']
                score = data[params][team]['points']
                
                if team != 9:
                    leaderboards += f'''
[{rank}]    {teamname}: {score}
'''
                else:
                    leaderboards += f'''
[{rank}]   {teamname}: {score}
'''
            await ctx.send(f''':triangular_flag_on_post:  **{params} CTFtime Leaderboards**```ini
{leaderboards}```''')
        
        if status == 'current':
            # THIS IS A MESS HELP ME ANYONE WHO SEES THIS D:
            # This is not a joke, please message me if you know how to fix this. 
            headers = {
                    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0',
                    }
            upcoming = 'https://ctftime.org/api/v1/events/'
            limit = '5'
            response = requests.get(upcoming, headers=headers, params=limit)
            json_data = response.json()
            data = []
            def update(name, entry):
                with open("db.json", mode='a', encoding='utf-8') as db:
                    json.dump(data, db, indent=3)

            with open("db.json", 'w') as db:
                #db_data = json.load(db)

                for num in range(0, int(limit)):
                    ctf_title = json_data[num]['title']
                    # local_ctftitle = db_data[num]['name']
                    
                    # if local_ctftitle not in ctf_title:
                    #     ctf_info = {
                    #         'name': db_data[num]['name'],
                    #         'start': db_data[num]['start'],
                    #         'end': db_data[num]['end'],
                    #         'dur': db_data[num]['dur'],
                    #         'url': db_data[num]['url'],
                    #         'img': db_data[num]['img'],
                    #         'format': db_data[num]['format']
                    #         }
                    #     data.append(ctf_info)

                    now = datetime.utcnow()
                    unix_now = int(now.replace(tzinfo=timezone.utc).timestamp())
                    ctf_format = json_data[num]['format']
                    ctf_place = json_data[num]['onsite']
                    
                    if ctf_place == False:
                        ctf_place = 'Online'
                    else:
                        ctf_place = 'Onsite'
                    
                    dur_dict = json_data[num]['duration']
                    (ctf_hours, ctf_days) = (str(dur_dict['hours']), str(dur_dict['days']))
                    (ctf_start, ctf_end) = (parse(json_data[num]['start'].replace('T', ' ').split('+', 1)[0]), parse(json_data[num]['finish'].replace('T', ' ').split('+', 1)[0]))
                    (unix_start, unix_end) = (int(ctf_start.replace(tzinfo=timezone.utc).timestamp()), int(ctf_end.replace(tzinfo=timezone.utc).timestamp()))
                    dur_dict = json_data[num]['duration']
                    (ctf_hours, ctf_days) = (str(dur_dict['hours']), str(dur_dict['days']))
                    ctf_link = json_data[num]['url']
                    ctf_image = json_data[num]['logo']
                    ctf_info = {
                        'name': ctf_title,
                        'start': unix_start,
                        'end': unix_end,
                        'dur': ctf_days+' days, '+ctf_hours+' hours',
                        'url': ctf_link,
                        'img': ctf_image,
                        'format': ctf_place+' '+ctf_format
                        }
                    data.append(ctf_info)
                    
            update('db.json', data)

            running = False
            #read from file and check if ctf is running
            with open("db.json") as db:
                data = json.load(db) #data, ctf['name'], ctf['start'], ctf['end'], ctf['dur'], ctf['url'], ctf['img'], ctf['format']
                
                for ctf in data:
                    now = datetime.utcnow()
                    unix_now = int(now.replace(tzinfo=timezone.utc).timestamp())
                    start = datetime.utcfromtimestamp(ctf['start']).strftime('%Y-%m-%d %H:%M:%S') + ' UTC'
                    end = datetime.utcfromtimestamp(ctf['end']).strftime('%Y-%m-%d %H:%M:%S') + ' UTC'
                  
                    if ctf['start'] < unix_now and ctf['end'] > unix_now: #check if ctf is currently running
                        print('test')
                        running = True
                        embed = discord.Embed(title=':red_circle: ' + ctf+' IS LIVE', description=url, color=15874645)
                     
                        if ctf['img'] != '':
                            embed.set_thumbnail(url=img)
                        else:
                            embed.set_thumbnail(url=default_image)
                         
                        embed.add_field(name='Duration', value=ctf['dur'], inline=True)
                        embed.add_field(name='Format', value=ctf['format'], inline=True)
                        embed.add_field(name='─' * 23, value=start+' -> '+end, inline=True)
                        await ctx.channel.send(embed=embed)
                        
            if running == False:
                await ctx.send("This command is currently broken along with ctf timeleft (I'm working on it!). In the meantime, check out >ctf countdown, and >ctftime upcoming to see when ctfs will start!")
 
        
        if status not in current_ctftime_cmds:
            await ctx.send('Current ctftime commands are: top [year], upcoming [amount up to 5], current')

    @commands.command()
    async def htb(self, ctx):
        twitter_page = requests.get('https://twitter.com/hackthebox_eu')
        all_content = str(twitter_page.text.encode('utf-8'))
        tweet = re.search('\\w+ will go live \\d{2}/\\d{2}/\\d{4} at \\d{2}:\\d{2}:\\d{2} UTC', all_content)
        match = tweet.group(0)
        await ctx.send(match + '\nhttps://hackthebox.eu')

def setup(bot):
    bot.add_cog(Ctfs(bot))