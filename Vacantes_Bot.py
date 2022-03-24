from pdb import Restart
from sqlite3 import Date
import sys
import os
import discord
import os
import requests
import json
import random
import configparser
import asyncio

#py -3 -m pip install -U discord.py
from discord import utils, client
from discord.ext import commands
from discord.ext.commands import bot
from datetime import date, datetime

#pip install telethon
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.messages import (GetHistoryRequest)
from telethon.tl.types import (
    PeerChannel
)

#pip install replit and dotenv
from replit import db # So yo can use it on a replit server later on
from dotenv import load_dotenv 

# Functions to parse json date to order it later
class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        if isinstance(o, bytes):
            return list(o)

        return json.JSONEncoder.default(self, o)


# Reading Configs to get credentials from telegram
config = configparser.ConfigParser()
config.read("config.ini")

# Setting configuration values
api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']

api_hash = str(api_hash)

phone = config['Telegram']['phone']
username = config['Telegram']['username']

# Create the client and connect
client = TelegramClient(username, api_id, api_hash)

async def main(phone):
    await client.start()
    print("Client Created")
    # Ensure you're authorized
    if await client.is_user_authorized() == False:
        await client.send_code_request(phone)
        try:
            await client.sign_in(phone, input('Enter the code: '))
        except SessionPasswordNeededError:
            await client.sign_in(password=input('Password: '))

    me = await client.get_me()

# Get the url or id from the group you wanna get the content from (This can be set to a fixed url or id)
    user_input_channel = input("Enter telegram URL or entity id: ")

    if user_input_channel.isdigit():
        entity = PeerChannel(int(user_input_channel))
    else:
        entity = user_input_channel

    my_channel = await client.get_entity(entity)

    offset_id = 0
    limit = 100
    all_messages = []
    total_messages = 0
    total_count_limit = 0
    
#Getting all the message with a limit of 100 per fetch and dumping it into a json file
    while True:
        print("Current Offset ID is:", offset_id, "; Total Messages:", total_messages)
        history = await client(GetHistoryRequest(
            peer=my_channel,
            offset_id=offset_id,
            offset_date=None,
            add_offset=0,
            limit=limit,
            max_id=0,
            min_id=0,
            hash=0
        ))
        if not history.messages:
            break
        messages = history.messages
        for message in messages:
            all_messages.append(message.to_dict())
        offset_id = messages[len(messages) - 1].id
        total_messages = len(all_messages)
        if total_count_limit != 0 and total_messages >= total_count_limit:
            break

    with open('messages.json', 'w') as outfile:
        json.dump(all_messages, outfile, cls=DateTimeEncoder)

with client:
    client.loop.run_until_complete(main(phone))

# Getting all the info from messages json file
with open('messages.json') as f:
    			data = json.load(f)

# Function to update the lastdate json file so it can always have the last date to compare in a new iteration
def Lastdatefun():
    # Getting info from last date json file
    with open('lastdate.json') as j:
                oldata = json.load(j)

    # Transforming last date from json to int 
    Lastyeardate = int(oldata[0:4])  
    Lastmonthdate = int(oldata[5:7]) 
    Lastdaydate = int(oldata[8:10]) 

    # Transform lastdate time to int
    Lastdatehour = int(oldata[11:13])
    Lastdateminute = int(oldata[14:16])
    Lastdatesecs = int(oldata[17:19])

    # Combine previous int data types into a datetime data type 
    Lastdatetime = datetime(Lastyeardate, Lastmonthdate, Lastdaydate, Lastdatehour, Lastdateminute, Lastdatesecs)

    return Lastdatetime
  



# Function to order all the last messages and dates from the json file and put them into a list
def OrderMessages(data, Vacante, Lastdatetime):
    for data in data:
        try:  
            Last_Vacante = data['message']
            VacanteDate = data['date']
            Vacanteyeardate = int(VacanteDate[0:4])  
            Vacantemonthdate = int(VacanteDate[5:7]) 
            Vacantedaydate = int(VacanteDate[8:10])
            Vacantedatehour = int(VacanteDate[11:13])
            Vacantedateminute = int(VacanteDate[14:16])
            Vacantedatesecs = int(VacanteDate[17:19])
            VacanteDatetime = datetime(Vacanteyeardate,Vacantemonthdate,Vacantedaydate, Vacantedatehour, Vacantedateminute, Vacantedatesecs)
            
            if Lastdatetime != VacanteDatetime and Lastdatetime < VacanteDatetime:
                Vacante.append(VacanteDate[0:10] + " / " + VacanteDate[11:19])
                Vacante.append(Last_Vacante)
                
              
            
        except KeyError: 
            break

    return Vacante 



#Load hidden Token from .env file (This is the token for the bot)
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
        
#Discord Client Start
client = discord.Client()

#Discord event when the bot is ready (This is when the bot is online)
@client.event
async def on_ready():
  print("We have logged in as {0.user}".format(client))
  
  channel = client.get_channel(956083383606333471)
  
#As soon as the bot goes online it will messages previously stored and ordered into the channel selected
#If no new messages were detected then it will send an apology message to the channel selected
  Vacantes = []
  Lastdatetime = Lastdatefun()
  Vacantes = OrderMessages(data,Vacantes,Lastdatetime)
  if Vacantes == []: await channel.send(str("**No ha habido vacantes nuevas recientemente :(**"))
  
  else: 
      for vacante in Vacantes:
        if vacante != []:
            await channel.send(str(vacante) + "\n" + "--------------------------------------------------------------------------------------------")
      await channel.send(str("**Estas han sido las vacantes de tecnologia mas recientes, buenas noches ;)**"))         
            
  with open('lastdate.json', 'w') as outfile:
            json.dump(str(data[0]['date']), outfile, cls=DateTimeEncoder)
            
       
# After sending all the new messages the bot will be turned off (External tool task manager is recommended to automate this process)
  await client.close();         
client.run(TOKEN)

