# ADMIN COMMANDS

# Handles all administrator commands

# IMPORT MODULES
import discord
import psycopg2
from modules import adminverify, recognudges

# VARIABLES
moduleVersion = 1.0
triggerWords = ["MOD", "MODERATOR", "ADMIN", "ADMINISTRATOR", "BIND", "BINDING"]

# INITIALIZE
def initialize(cl, co):
    
    # DEBUG 
    print ("> Initializing Module: Administrator Commands")
    
    # PASS IN VARIABLES
    global conn
    global cursor
    global client
    
    conn = co
    cursor = conn.cursor()
    client = cl
    
# RETURN INFO
def getInfo():
    
    # CREATE VARIABLES
    information = {
        "name" : "Admin Commands", 
        "moduleVersion" : moduleVersion,
        "triggerWords" : triggerWords
    }
    
    return(information)


async def handleMessage(message, messageInfo, subject, sentence, sentID):
    
    # COLLECT RELEVANT INFORMATION
    channel = message.channel
    author = message.author
    embedColor = message.guild.me.colour
    adminPrivilleges = adminverify.verify(author)
    
    
    # SORT FOR COMMANDS
    if (subject == "ADMINISTRATOR" or subject == "ADMIN"):
        
        if ("ROLE" in sentence):                # SET MOD ROLE POSITION
            
            # SEND AN ERROR EMBED
            embed = discord.Embed (
                title = "Naming Clarification",
                color = embedColor,
                description = str(
                    '''This command does not exist. If you're looking to setup *Moderator Roles*, use: \n
                    `Morgann, set the mod role to @role`.'''
                )
            )
            
            embed.add_field (
                name = "**WHAT'S THE DIFFERENCE?**", 
                value = '''An **Administrator** is a permission tier granted only by a role's permissions (within a server), and allows you access to high-level commands of mine. \n
                A **Moderator** is a less-powerful tier I can grant that allows you to manage me without all the danger of administrative permissions. ''',
                inline = False
            )
            
            embed.set_footer(text = "Still confused? Ask for help with admin/mod permissions")

            await recognudges.nudgeClear(message)
            await channel.send(embed = embed)
            return
    


    elif (subject == "MODERATOR" or subject == "MOD"):
        
        if ("ROLE" in sentence):                # SET MOD ROLE POSITION
            
            # CHECK PERMISSION LEVEL
            if (adminPrivilleges[0] == False):
                
                # SEND AN ERROR EMBED
                embed = discord.Embed (
                    title = "Invalid Permissions",
                    color = embedColor,
                    description = str(
                        '''You do not have permission to use this command. You must be the **Server Owner** or an **Administrator** to do so.'''
                    )
                )
                
                await recognudges.nudgeClear(message)
                await channel.send(embed = embed)
                return
            
            elif (adminPrivilleges[1] < 2):
                
                # SEND AN ERROR EMBED
                embed = discord.Embed (
                    title = "Invalid Permissions",
                    color = embedColor,
                    description = str(
                        '''You do not have permission to use this command. You must be the **Server Owner** or an **Administrator** to do so.'''
                    )
                )
                
                embed.set_footer(text = "Confused? Ask for help with admin/mod permissions")
                
                await recognudges.nudgeClear(message)
                await channel.send(embed = embed)
                return
            
            
            # CHECK FOR ROLE MENTIONS
            if (len(message.role_mentions) == 0):
                
                # SEND AN ERROR EMBED
                embed = discord.Embed (
                    title = "No Role Mentioned",
                    color = embedColor,
                    description = str(
                        '''You must to @mention a role to set it as a Moderator. If you're having trouble, ensure you can @mention the role in its settings. '''
                    )
                )
                
                await recognudges.nudgeClear(message)
                await channel.send(embed = embed)
                return
            
            
            # SETUP MODERATOR ROLE
            sql = "UPDATE guildinfo SET modroleposition = %s WHERE id = %s"
            val = (message.role_mentions[0].position, message.guild.id, )
            cursor.execute(sql, val)
            conn.commit()
            
            # RETURN EMBED
            embed = discord.Embed (
                title = "Moderator Role Setup Complete",
                color = embedColor,
                description = str(
                    '''Everyone with the role **@''' + message.role_mentions[0].name + '''** and above are now Moderators.'''
                )
            )

            await recognudges.nudgeClear(message)
            await channel.send(embed = embed)
            return



    elif (subject == "BIND" or subject == "BINDING"):

        # CHECK PERMISSIONS 
        if (adminPrivilleges[0] == False):

            # SEND ERROR EMBED
            embed = discord.Embed (
                    title = "Invalid Permissions",
                    color = embedColor,
                    description = str(
                        '''You do not have permission to use these commands. You must be a **Moderator** or an **Administrator** to do so.'''
                    )
                )
            
            await recognudges.nudgeClear(message)
            await channel.send(embed = embed)
            return

        
        if ("OFF" in sentence or "DISABLE" in sentence):    # BIND OFF

            # UPDATE DATABASE
            sql = "UPDATE guildinfo SET boundspace = %s, boundiscategory = %s WHERE id = %s"
            val = (0, False, message.guild.id, )
            cursor.execute(sql, val)
            conn.commit()

            # SEND SUCCESS EMBED
            embed = discord.Embed (
                title = "Removed Binding",
                color = embedColor,
                description = str(
                    '''I'm no longer bound to a channel or category. Now time to bring in the chaos...'''
                )
            )

            embed.set_footer(text = "I'm kidding, of course. Or am I?")

            await recognudges.nudgeClear(message)
            await channel.send(embed = embed)
            return


        elif ("CHANNEL" in sentence):                # BIND TO CHANNEL

            if ("THIS" in sentence):

                # UPDATE DATABASE
                sql = "UPDATE guildinfo SET boundspace = %s, boundiscategory = %s WHERE id = %s"
                val = (channel.id, False, message.guild.id, )
                cursor.execute(sql, val)
                conn.commit()

                # SEND SUCCESS EMBED
                embed = discord.Embed (
                    title = "Changed Bound Channel",
                    color = embedColor,
                    description = str(
                        '''**#''' + channel.name + '''** is now the only channel I'll operate in.'''
                    )
                )

                await recognudges.nudgeClear(message)
                await channel.send(embed = embed)
                return
            
            # CHECK FOR CHANNEL MENTIONS
            if (len(message.mentions.channelMentions) == 0):

                # SEND ERROR EMBED
                embed = discord.Embed (
                    title = "No Channel Mentioned",
                    color = embedColor,
                    description = str(
                        '''I couldn't find **#channel mention** in your message.'''
                    )
                )

                embed.set_footer(text = "Try #mentioning a channel next time")

                await recognudges.nudgeClear(message)
                await channel.send(embed = embed)
                return

            channelBind = message.mentions.channelMentions[0]

            # UPDATE DATABASE
            sql = "UPDATE guildinfo SET boundspace = %s, boundiscategory = %s WHERE id = %s"
            val = (channelBind.id, False, message.guild.id, )
            cursor.execute(sql, val)
            conn.commit()

            # SEND SUCCESS EMBED
            embed = discord.Embed (
                title = "Changed Bound Channel",
                color = embedColor,
                description = str(
                    '''**#''' + channelBind.name + '''** is now the only channel I'll operate in.'''
                )
            )

            await recognudges.nudgeClear(message)
            await channel.send(embed = embed)
            return

        elif ("CATEGORY" in sentence):                # BIND TO CATEGORY

            if ("THIS" in sentence):

                # CHECK IF CATEGORY EXISTS
                if (channel.category == None):

                    # SEND ERROR EMBED
                    embed = discord.Embed (
                        title = "No Category Found",
                        color = embedColor,
                        description = str(
                            '''This channel is not part of a category, and I can't bind to nothing.'''
                        )
                    )

                    embed.set_footer(text = "Try #mentioning a channel in a category next time")
                
                    await recognudges.nudgeClear(message)
                    await channel.send(embed = embed)
                    return

                # UPDATE DATABASE
                sql = "UPDATE guildinfo SET boundspace = %s, boundiscategory = %s WHERE id = %s"
                val = (channel.category.id, True, message.guild.id, )
                cursor.execute(sql, val)
                conn.commit()

                # SEND SUCCESS EMBED
                embed = discord.Embed (
                    title = "Changed Bound Category",
                    color = embedColor,
                    description = str(
                        '''**#''' + channel.category.name + '''** is now the only category of channels I'll operate in.'''
                    )
                )

                await recognudges.nudgeClear(message)
                await channel.send(embed = embed)
                return
            
            # CHECK FOR CHANNEL MENTIONS
            if (len(message.mentions.channelMentions) == 0):

                # SEND ERROR EMBED
                embed = discord.Embed (
                    title = "No Channel Mentioned",
                    color = embedColor,
                    description = str(
                        '''I couldn't find **#channel mention** in your message.'''
                    )
                )

                embed.set_footer(text = "Try #mentioning a channel next time")
            
                await recognudges.nudgeClear(message)
                await channel.send(embed = embed)
                return

            categoryBind = message.mentions.channelMentions[0].category

            # CHECK IF CATEGORY EXISTS
            if (categoryBind == None):

                # SEND ERROR EMBED
                embed = discord.Embed (
                    title = "No Category Found",
                    color = embedColor,
                    description = str(
                        '''This channel is not part of a category, and I can't bind to nothing.'''
                    )
                )

                embed.set_footer(text = "Try #mentioning a channel in a category next time")
            
                await recognudges.nudgeClear(message)
                await channel.send(embed = embed)
                return


            # UPDATE DATABASE
            sql = "UPDATE guildinfo SET boundspace = %s, boundiscategory = %s WHERE id = %s"
            val = (categoryBind.id, True, message.guild.id, )
            cursor.execute(sql, val)
            conn.commit()

            # SEND SUCCESS EMBED
            embed = discord.Embed (
                title = "Changed Bound Category",
                color = embedColor,
                description = str(
                    '''**#''' + categoryBind.channel.name + '''** is now the only category of channels I'll operate in.'''
                )
            )

            await recognudges.nudgeClear(message)
            await channel.send(embed = embed)
            return

    await recognudges.nudgeConfused(message)