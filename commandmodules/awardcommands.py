# AWARD COMMANDS

# Handles commands for awards

# IMPORT MODULES
import discord
import psycopg2
import random

# VARIABLES
moduleVersion = 2.0
triggerWords = ["AWARD"]


# INITALIZE
def initialize(c, co):
    
    # DEBUG
    print("> Initializing Module: Award Commands")
    
    # PASS IN VARIABLES
    global client
    global conn
    global cursor
    
    client = c
    conn = co
    cursor = conn.cursor()
    
# RETURN INFO
def getInfo():
    
    # CREATE VARIABLES
    information = {
        "name" : "Award Commands", 
        "moduleVersion" : moduleVersion,
        "triggerWords" : triggerWords
    }
    
    return(information)

async def handleMessage(message, messageInfo, subject, sentence, sentID):
    
    # COLLECT RELEVANT INFORMATION
    channel = message.channel
    author = message.author
    embedColor = message.guild.me.colour
    
    
    # SORT FOR COMMANDS
    if (subject == "AWARD"):
        
        # CHECK FOR TOPIC
        if ("ADD" in sentence or "CREATE" in sentence):     # CREATE AN AWARD TYPE
            
            print("nice")