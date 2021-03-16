# SANDWICH SHARING COMMANDS

# Handles commands for the sandwhich sharing module

# IMPORT MODULES
import discord
import json
import random
import asyncio
from modules import recognudges


# VARIABLES
moduleVersion = 2.0
triggerWords = ["SANDWICH", "SANDWHICH"]
numberEmojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]

# LOAD DATA
with open ("./savefiles/sandwiches/sandwiches.json", "r") as file:
    lines = file.readlines()
    string = "\t".join([line.strip() for line in lines])
    sandwiches = json.loads(string)["sandwiches"]
file.close()

with open ("./savefiles/sandwiches/condiments.json", "r") as file:
    lines = file.readlines()
    string = "\t".join([line.strip() for line in lines])
    condiments = json.loads(string)["condiments"]
file.close()

with open ("./savefiles/sandwiches/breads_and_pastries.json", "r") as file:
    lines = file.readlines()
    string = "\t".join([line.strip() for line in lines])
    breads = json.loads(string)["breads"]
file.close()

with open ("./savefiles/sandwiches/iba_cocktails.json", "r") as file:
    lines = file.readlines()
    string = "\t".join([line.strip() for line in lines])
    cocktails = json.loads(string)["cocktails"]
file.close()


# INITALIZE
def initialize(c):
    
    # DEBUG
    print("> Initializing Module: Sandwhich Commands")

    global client
    client = c

    
# RETURN INFO
def getInfo():
    
    # CREATE VARIABLES
    information = {
        "name" : "Sandwich Commands", 
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
    if (subject == "SANDWICH" or subject == "SANDWHICH"):

        # CHECK FOR TOPIC
        if ("MAKE" in sentence):                 # MAKE A SANDWICH

            # COMPILE RANDOM SANDWICH
            sandwich = sandwiches[random.randrange(0, len(sandwiches))]
            bread = breads[random.randrange(0, len(breads))]
            condiment = condiments[random.randrange(0, len(condiments))]
            cocktail = cocktails[random.randrange(0, len(cocktails))]

            # COMPOSE EMBED
            embed = discord.Embed (
                title = "Here's Your Sandwich!",
                color = embedColor,
                description = "**" + sandwich["name"] + " Sandwich** Made from **" + bread.capitalize() + " Bread**"
            )

            embed.add_field (
                name = "Description",
                value = sandwich["description"],
                inline = True
            )

            embed.add_field (
                name = "Optional Extras",
                value = str(
                    '''
                    Extra Condiment: **''' + condiment + '''**
                    Optional Cocktail: **''' + cocktail + '''**
                    ''')
            )

            await recognudges.nudgeClear(message)
            await channel.send(embed = embed)
            return

        elif ("SUBMIT" in sentence or "SHARE" in sentence):             # SHARE A SANDWICH
            
            # RESPOND ASKING FOR SANDWICH INFORMATION
            embed = discord.Embed (
                title = "Describe your Sandwich",
                color = embedColor,
                description = "Give us a quick description of your sandwich"
            )

            await recognudges.nudgeClear(message)
            await message.delete()
            infoMessage = await channel.send(embed = embed)

            # AWAIT RESPONSE
            def responseCheck(message):
                return message and message.author == author

            try: 
                message = await client.wait_for('message', timeout = 360.0, check = responseCheck)
            except asyncio.TimeoutError:
                await infoMessage.delete()

            description = message.content

            # ASK FOR EATEN %
            embed = discord.Embed (
                title = "Describe How Much You've Eaten",
                color = embedColor,
                description = "On a scale of 1-5, how much of your sandwich have you eaten?"
            )

            await message.delete()
            await infoMessage.delete()
            eatenMessage = await channel.send(embed = embed)

            for emoji in numberEmojis:
                await eatenMessage.add_reaction(emoji)

            # AWAIT RESPONSE
            def eatenCheck(reaction, member):
                return reaction and member == message.author

            try: 
                reaction, member = await client.wait_for('reaction_add', timeout = 60.0, check = eatenCheck)
            except asyncio.TimeoutError:
                await eatenMessage.delete()

            # COMPILE ANNOUNCEMENT MESSAGE
            embed = discord.Embed (
                title = "@" + author.display_name + " Wants to Share Their Sandwich!",
                color = embedColor,
                description = str(
                    '''
                    **Description:** ''' + description + '''
                    **Eaten Amount:** ''' + str(reaction.emoji)
                )
            )

            await eatenMessage.delete()
            announcementsChannel = message.guild.get_channel(821362461080027176)
            announceMessage = await announcementsChannel.send(embed = embed)

            await announceMessage.add_reaction("✅")

            # AWAIT REACTION
            def dmCheck(reaction, member):
                return reaction.emoji == "✅" and member != announceMessage.guild.me and reaction.message == announceMessage

            reaction, member = await client.wait_for('reaction_add', check = dmCheck)

            # DM THE USER
            embed = discord.Embed (
                title = "Here's Your Sandwich!",
                color = embedColor,
                description = str(
                    '''
                    Contact **@''' + author.display_name + '''** to claim your sandwich
                    '''
                )
            )

            await member.send(embed = embed)
            await announceMessage.delete()