# MORGANN MAIN

# Handles front-end user interaction & messages

# IMPORT MODULES
import discord
import logging
import psycopg2
import os
import asyncio
import datetime
import random
import json

from modules import nltkpreprocessor as preprocessor
from modules import insultmanager, quotemanager, guildmanager, adminverify, recognudges
from commandmodules import helpcommands, insultcommands, awardcommands, quotecommands, admincommands, japcommands

logging.basicConfig(level = logging.WARNING)

# VARIABLES
client = discord.Client()
clientVersion = 2.0


# LOAD DATA
with open ("./savefiles/config.txt", "r") as file:
    lines = file.readlines()
    string = "\t".join([line.strip() for line in lines])
    configOptions = json.loads(string)
file.close()

# CONNECT TO DB
conn = psycopg2.connect(configOptions["dbURL"], sslmode = "require")
cursor = conn.cursor()


# DISCORD EVENTS
@client.event
async def on_ready():
    
    # DEBUG 
    print("> Morgann Online & Connected")
    
    # UPDATE STATUS
    await client.change_presence(
        activity = discord.Game("with your emotions"),
        status = discord.Status.online, 
        afk = False
    )
    
    

@client.event
async def on_guild_join(guild):
    
    # DELEGATE TO GUILD MANAGER
    await guildmanager.guildJoin(guild)
    
@client.event 
async def on_guild_remove(guild):
    
    # DELEGATE TO GUILD MANAGER
    await guildmanager.guildLeave(guild)
    
    
@client.event
async def on_raw_reaction_add(payload):
    
    # CHECK REACTION TYPE
    if (str(payload.emoji) == '📌'):
        
        # HANDLE WITH QUOTE MANAGER
        await quotemanager.quoteMessage(payload)
    
    
    
@client.event
async def on_message(message):

    # CHECK IF SENT BY SELF
    if (message.author == message.guild.me):
        return
    
    # RETRIEVE SERVER INFORMATION
    sql = "SELECT * FROM guildinfo WHERE id = %s"
    val = (message.guild.id, )
    cursor.execute(sql, val)
    guildInfo = cursor.fetchone()
    
    # CHECK IF IN BOUND CHANNEL
    if not (guildInfo[3] == 0 or guildInfo[3] == None):
        if (guildInfo[7] == None or guildInfo[7] == False):
            if (not message.channel.id == guildInfo[3]):
                return
        else:
            if (not message.channel.category == None):
                if (not message.channel.category.id == guildInfo[3]):
                    return
        
    # HANDLE INSULTS
    await insultmanager.handleInsults(message, guildInfo)
    
    # CHECK IF MENTIONED
    for alias in configOptions["aliases"]:
        if (alias in message.content.upper()):
            break
    else:
        if not(len(message.mentions) > 0 and message.mentions[0] == message.guild.me):
            return

    # ADD RECOGNITION NUDGE
    await recognudges.nudgeAware(message)
    
    # PREPROCESS MESSAGE
    messageInfo = preprocessor.preprocessMessage(message)
    print(messageInfo)
    
    # CHECK FOR CONTENT
    if (messageInfo["tokenized"] == [[]]):
        return
    
    # SEARCH KNOWN MODULES 
    sentNo = 0
    while sentNo < len(messageInfo["final"]):
        sent = messageInfo["final"][sentNo]
        
        # CHECK FOR NO CONTENT
        if (sent == []):
            continue
            
        for module in loadedModules:
            
            moduleInfo = module.getInfo()
            
            for word in moduleInfo["triggerWords"]:
                if (word in sent):

                    # ADD NUDGE
                    await recognudges.nudgeThink(message)
                    
                    # DELEGATE TO MODULE
                    await module.handleMessage(message, messageInfo, word, sent, sentNo)
                    return
        
        sentNo += 1

    
# INIT MODULES
loadedModules = [helpcommands, insultcommands, awardcommands, quotecommands, admincommands, japcommands]
helpcommands.initialize(client)
insultcommands.initialize(client, conn)
awardcommands.initialize(client, conn)
quotecommands.initialize(client, conn)
admincommands.initialize(client, conn)
recognudges.initialize()
japcommands.initialize()

preprocessor.initialize(configOptions["aliases"])
insultmanager.initialize(conn, client)
quotemanager.initialize(conn, client)
guildmanager.initialize(conn, client)
adminverify.initialize(conn, client)


# RUN
print("> Starting Morgann")
client.run(configOptions["clientKey"])