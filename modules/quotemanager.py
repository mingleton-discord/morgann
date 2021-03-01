# QUOTE MANAGER

# Handles quote asynchronously

# IMPORT MODULES
import discord
import psycopg2
import random 
import asyncio

# VARIABLES
moduleVersion = 2.0

# INITIALIZE
def initialize(co, cl):
    
    # DEBUG 
    print ("> Initializing Module: Quote Manager")
    
    # INIT VARIABLES
    global conn
    global cursor
    global client
    
    conn = co
    cursor = conn.cursor()
    client = cl
    
    # INIT BACKGROUND LOOP
    client.loop.create_task(dailyQuoteUpdate())
    
    
async def dailyQuoteUpdate():
    
    await client.wait_until_ready()
    while(True):
        
        # DEBUG
        print("> Running Daily Quote Update...")
        
        # UPDATE EVERY DAILY QUOTE
        async for guild in client.fetch_guilds(limit = None):
            
            # FETCH SQL
            sql = "SELECT dqchannelid, dqmessageid FROM guildinfo WHERE id = %s" 
            val = (guild.id, )
            cursor.execute(sql, val)
            guildInfo = cursor.fetchone()
            
            if (guildInfo == None):
                continue
            
            if (guildInfo[0] == 0 or guildInfo[1] == 0):
                continue
                
            # FETCH MESSAGE OBJECT
            channel = client.get_channel(guildInfo[0])
            if (channel == None):
                continue
            message = await channel.fetch_message(guildInfo[1])
            if (message == None):
                continue
            embedColor = message.guild.me.colour
                        
                
            # FETCH RANDOM QUOTE
            sql = "SELECT creatorid, content, authorname, authorid FROM quotes WHERE guildid = %s"
            val = (guild.id, )
            cursor.execute(sql, val)
            selectQuotes = cursor.fetchall()
            
            # COLLECT INFORMATION
            chosenQuote = selectQuotes[random.randrange(0, len(selectQuotes) - 1)]
            
            quoteCreator = ""
            qC = client.get_user(chosenQuote[0])
            if (qC == None):
                quoteCreator = "A fallen member..."
            else: 
                quoteCreator = "@" + qC.display_name
            
            quoteAuthor = ""
            if (chosenQuote[2] != None):
                quoteAuthor = chosenQuote[2]
            else:
                qA = client.get_user(chosenQuote[3])
                if (qA == None):
                    quoteAuthor = "A fallen member..."
                else:
                    quoteAuthor = "@" + qA.display_name
                    
            # GENERATE EMBED
            embed = discord.Embed (
                title = str(
                    '"' + chosenQuote[1] + '"'
                ),
                color = embedColor
            )
            
            embed.set_footer(text = str(
                "- " + quoteAuthor +
                " | Added by " + quoteCreator
            ))
            
            await message.edit(embed = embed)
            
        # DEBUG
        print("> Daily Quote Update Complete")
            
        await asyncio.sleep(86400)
    
    
async def quoteMessage(payload):
    
    # COLLECT RELEVANT INFORMATION
    channel = client.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    author = message.author
    embedColor = message.guild.me.colour
    
    # CHECK NUMBER OF REACTIONS
    for reaction in message.reactions:
        if (str(reaction.emoji) == "📌" and reaction.count > 2):
            break
    else: 
        return
    
    # CHECK IF CAN BE QUOTED
    if (message.content == "" or message.content == None):
        
        # SEND AN ERROR EMBED
        embed = discord.Embed (
            title = "Unable to Quote",
            color = embedColor,
            description = str(
                "This message doesn't have anything I'm able to quote."
            )
        )
        
        embed.set_footer(text = "The message must have text content to quote")
        await channel.send(embed = embed)
        return
    
    # ADD TO DB
    sql = "INSERT INTO quotes (quoteid, guildid, creatorid, version, content, authorid) VALUES (%s, %s, %s, %s, %s, %s)"
    val = (message.id, message.guild.id, payload.user_id, moduleVersion, message.clean_content, author.id)
    cursor.execute(sql, val)
    conn.commit()
    
    # SEND SUCCESS EMBED
    embed = discord.Embed (
        title = str(
            '"' + message.clean_content + '"'
        ),
        color = embedColor
    )
    
    embed.set_footer(text = str(
        "- @" + author.display_name + 
        " | Added"
    ))
    
    await channel.send(embed = embed)   
    