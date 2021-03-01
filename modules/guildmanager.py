# GUILD MANAGER

# Handles guild connections or disconnections

# IMPORT MODULES
import discord
import psycopg2

# VARIABLES
clientVersion = 2.0


# INITIALIZE
def initialize(co, cl):
    
    # DEBUG
    print("> Initializing Module: Guild Manager")
    
    # INIT VARIABLES
    global conn
    global cursor
    global client
    
    conn = co
    cursor = conn.cursor()
    client = cl
    

async def guildJoin(guild):
    
    # CHECK IF GUILD EXISTS
    sql = "SELECT * FROM guildinfo WHERE id = %s"
    val = (guild.id, )
    cursor.execute(sql, val)
    result = cursor.fetchone()
    
    if (result == None):
        
        # ADD GUILD
        sql = "INSERT INTO guildinfo (id, version) VALUES (%s, %s)"
        val = (guild.id, clientVersion, )
        cursor.execute(sql, val)
        conn.commit()
        
    else: 
        
        # DELETE EXISTING RECORDS
        sql = "DELETE FROM guildinfo WHERE id = %s"
        val = (guild.id, )
        cursor.execute(sql, val)
        
        # ADD NEW GUILD RECORD
        sql = "INSERT INTO guildinfo (id, version) VALUES (%s, %s)"
        val = (guild.id, clientVersion, )
        cursor.execute(sql, val)
        conn.commit()
        
    # GENERATE WELCOME EMBED
    embed = discord.Embed (
        title = str("Hi! I'm Morgann"),
        description = str(
            "Thanks for adding me to your server, now let's get started with setup."
        )
    )
    
    embed.add_field (
        name = "**🔗 CHANNEL BINDING**",
        value = str(
            "I can be bound to a specific channel or category to stop me from filling up unrelated channels." + 
            "```Morgann, bind to #bots```"
        ), 
        inline = False
    )
    
    embed.add_field (
        name = "**👑 ADMINISTRATOR SETUP**",
        value = str(
            "By default, any roles you specify as an `administrator` within your server's role settings will have administrator privileges, however you can setup other adminstators yourself." +
            "```Morgann, set @mods as adminstrators```" + 
            "Any role that appears higher in the role heirachy will also become an adminstrator role. \n \n" + 
            "*Only default moderators can change this setting in the future*"
        ), 
        inline = False
    )
    
    embed.add_field (
        name = "**💬 INSULT COOLDOWN**",
        value = str(
            "To avoid spam, you can setup a cooldown time for how often people will be insulted by me" +
            "```Morgann, set the insult cooldown to 2 minutes``` \n \n" +
            "**[coming soon]**"
        ), 
        inline = False
    )    
    
    # ATTEMPT TO SEND WELCOME EMBED
    if (guild.system_channel != None):
        
        # SEND TO THE PUBLIC UPDATES CHANNEL
        await guild.system_channel.send(embed = embed)
        

async def guildLeave(guild):
    
    # REMOVE FROM DATABASE
    sql = "DELETE FROM guildinfo WHERE id = %s"
    val = (guild.id, )
    cursor.execute(sql, val)
    conn.commit()
        