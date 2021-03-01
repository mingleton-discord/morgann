# JAPANESE COMMANDS

# Handles commands for the Old Japanese Saying module

# IMPORT MODULES
import discord
import json
import random
import asyncio
from modules import recognudges


# VARIABLES
moduleVersion = 2.0
triggerWords = ["SAYING"]
numberEmojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]

# LOAD DATA
with open ("./savefiles/japanesesayings.txt", "r") as file:
    lines = file.readlines()
    string = "\t".join([line.strip() for line in lines])
    japSayings = json.loads(string)
file.close()


# INITALIZE
def initialize():
    
    # DEBUG
    print("> Initializing Module: Japanese Saying Commands")

    
# RETURN INFO
def getInfo():
    
    # CREATE VARIABLES
    information = {
        "name" : "Japanese Saying Commands", 
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
    if (subject == "SAYING"):

        # GENERATE SAYING
        partOne = japSayings["parts"][random.randrange(0, len(japSayings["parts"]) - 1)]
        partTwo = japSayings["parts"][random.randrange(0, len(japSayings["parts"]) - 1)]
        conjoiner = japSayings["conjoiners"][random.randrange(0, len(japSayings["conjoiners"]) - 1)]

        japSaying = '"' + partOne.capitalize() + " " + conjoiner + " " + partTwo + '."'

        # GENERATE EMBED
        embed = discord.Embed (
            title = "There Was an Old Japanese Saying",
            color = embedColor,
            description = japSaying
        )

        # SEND MESSAGE
        await recognudges.nudgeClear(message)
        await channel.send(embed = embed)
        return