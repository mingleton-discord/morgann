# INSULT MANAGER

# Handles insults asynchronously

# IMPORT MODULES
import discord
import psycopg2
import random 
import asyncio

# VARIABLES
activeCooldowns = []


# INITIALIZE
def initialize(co, cl):
    
    # DEBUG 
    print ("> Initializing Module: Insult Manager")
    
    # INIT VARIABLES
    global conn
    global cursor
    global client
    
    conn = co
    cursor = conn.cursor()
    client = cl

    # INIT BACKGROUND LOOP
    client.loop.create_task(cooldownUpdate())
    

async def cooldownUpdate():

    # INITIAL RESET
    sql = "UPDATE guildinfo SET insultiscooldown = %s"
    val = (False, )
    cursor.execute(sql, val)

    await client.wait_until_ready()
    while(True):

        for id, cooldown in enumerate(activeCooldowns):

            if (cooldown["cooldownCycles"] < 1):

                sql = "UPDATE guildinfo SET insultiscooldown = %s WHERE id = %s"
                val = (False, cooldown["guildID"], )
                cursor.execute(sql, val)

                activeCooldowns.pop(id)

            else:

                cooldown["cooldownCycles"] -= 1

        conn.commit()
        await asyncio.sleep(60)


    
async def handleInsults(message, guildInfo):
    
    # COLLECT RELEVANT INFORMATION
    channel = message.channel
    author = message.author
    embedColor = message.guild.me.colour

    # CHECK IF COOLDOWN IS ACTIVE
    if (guildInfo[8] == True):
        return
    
    # CHECK IF A USER IS TARGETED
    if (author.id == guildInfo[2]):
        
        # GET ALL SERVER INSULTS
        sql = "SELECT authorid, content, receiverid FROM insults WHERE guildid = %s AND receiverid = 0"
        val = (message.guild.id, )
        cursor.execute(sql, val)
        guildInsults = cursor.fetchall()
        
        # GET MEMBER-SPECIFIC INSULTS
        sql = "SELECT authorid, content, receiverid FROM insults WHERE guildid = %s AND receiverid = %s"
        val = (message.guild.id, author.id)
        cursor.execute(sql, val)
        memberInsults = cursor.fetchall()
        
        # COMPILE INSULTS
        selectInsults = []
        if (len(memberInsults) < 5):
            # ADD MEMBER INSULTS TO SERVER INSULTS
            selectInsults = guildInsults + memberInsults
        else: 
            # JUST USE MEMBER INSULTS
            selectInsults = memberInsults
        
        # COLLECT INFORMATION
        chosenInsult = selectInsults[random.randrange(0, len(selectInsults) - 1)]
        insultAuthor = client.get_user(chosenInsult[0])
        
        # GENERATE EMBED
        embed = discord.Embed (
            title = chosenInsult[1],
            color = embedColor
        )
        
        if (insultAuthor != None):
            if (chosenInsult[2] == 0):
                embed.set_footer(text = str("Added by @" + insultAuthor.display_name))
            else:
                embed.set_footer(text = str("Added by @" + insultAuthor.display_name + " just for you"))
        else:
            embed.set_footer(text = "Added by a fallen member...")
            
        # SEND EMBED
        await channel.send(embed = embed)

        if (guildInfo[9] > 0):
            # CREATE COOLDOWN OBJECT
            cooldown = {
                "guildID" : message.guild.id,
                "cooldownCycles" : guildInfo[9]
            }

            activeCooldowns.append(cooldown)

            # UPDATE SERVER
            sql = "UPDATE guildinfo SET insultiscooldown = %s WHERE id = %s"
            val = (True, message.guild.id, )
            cursor.execute(sql, val)
            conn.commit()
