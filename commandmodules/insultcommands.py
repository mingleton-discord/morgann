# INSULT COMMANDS

# Handles commands for insults

# IMPORT MODULES
import discord
import psycopg2
import random
import asyncio
from modules import adminverify, recognudges

# VARIABLES
moduleVersion = 2.0
triggerWords = ["INSULT", "TARGET", "TARGETING", "TARGETTING"]
numberEmojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]


# INITALIZE
def initialize(c, co):
    
    # DEBUG
    print("> Initializing Module: Insult Commands")
    
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
        "name" : "Insult Commands", 
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
    if (subject == "INSULT"):
        
        # CHECK FOR TOPIC
        if ("ADD" in sentence):             # ADD AN INSULT
            
            # GET GUILD INFO
            sql = "SELECT targeteduserid FROM guildinfo WHERE id = %s"
            val = (message.guild.id, )
            cursor.execute(sql, val)
            targetedUserID = cursor.fetchone()[0]

            # CHECK PERMISSIONS
            adminPrivilleges = adminverify.verify(author)

            if (adminPrivilleges[0] == False and targetedUserID == 0):

                # SEND ERROR EMBED
                embed = discord.Embed ( 
                    title = "Invalid Permisssions",
                    color = embedColor,
                    description = str(
                        '''You do not have permission to use this command at the moment. You must be a **Moderator** or **Administrator** to do so.'''
                    )
                )

                await recognudges.nudgeClear(message)
                await channel.send(embed = embed)
                return

            # FIND INSULT FOR SENTENCE
            insult = ""
            for quote in messageInfo["quotes"]:
                
                if (quote["sentID"] == sentID):
                    
                    insult = quote["quote"].capitalize()
                    break
                    
            else: 
                    
                # SEND ERROR EMBED
                embed = discord.Embed (
                    title = "No Insult Found",
                    color = embedColor,
                    description = str(
                        '''Try using `"` around the insult. For example, `"You're really bad at adding insults"`'''
                    )
                )

                await recognudges.nudgeClear(message)
                await channel.send(embed = embed)
                return
            
            
            # CHECK FOR A RECEIVER
            receiverid = 0
            if (len(messageInfo["mentions"]["userMentions"]) > 0):
                receiverid = messageInfo["mentions"]["userMentions"][0].id
                    
            
            # ADD INSULT TO DB
            sql = "INSERT INTO insults (insultid, guildid, authorid, version, content, receiverid) VALUES (%s, %s, %s, %s, %s, %s)"
            val = (message.id, message.guild.id, author.id, moduleVersion, insult, receiverid,)
            cursor.execute(sql, val)
            conn.commit()
            
            
            # SEND EMBED
            embed = discord.Embed (
                title = insult,
                color = embedColor
            )
            
            if (receiverid == 0):
                embed.set_footer(text = "Added")
            else:
                embed.set_footer(text = str("Added for @" + messageInfo["mentions"]["userMentions"][0].display_name))
            
            await recognudges.nudgeClear(message)
            await channel.send(embed = embed)
            return
            
        
        
        elif ("RANDOM" in sentence):        # SELECT RANDOM INSULT
            
            # GET ALL SERVER INSULTS
            sql = "SELECT authorid, content, receiverid FROM insults WHERE guildid = %s"
            val = (message.guild.id, )
            cursor.execute(sql, val)
            selectInsults = cursor.fetchall()
                
            # COLLECT INFORMATION
            chosenInsult = selectInsults[random.randrange(0, len(selectInsults) - 1)]
            insultAuthor = client.get_user(chosenInsult[0])
            insultReceiver = client.get_user(chosenInsult[2])

            # GENERATE EMBED
            embed = discord.Embed(
                title = chosenInsult[1],
                color = embedColor
            )

            if (insultAuthor != None):
                if (chosenInsult[2] == 0 or insultReceiver == None):
                    embed.set_footer(text = str("Added by @" + insultAuthor.display_name))
                else:
                    embed.set_footer(text = str("Added by @" + insultAuthor.display_name + " for @" + insultReceiver.display_name))
            else:
                embed.set_footer(text = "Added by a fallen member...")

            # SEND EMBED
            await channel.send(embed = embed)
            
            
            
        elif ("SEARCH" in sentence):          
            
            # CHECK FOR QUERIES
            if (len(messageInfo["quotes"]) == 0 and len(messageInfo["mentions"]["userMentions"]) == 0):
                
                # SEND ERROR EMBED
                embed = discord.Embed ( 
                    title = "No Search Terms Found",
                    color = embedColor,
                    description = str(
                        '''Try **@mentioning** someone, or using `"` around your search terms so that I can detect them.'''
                    )
                )
                
                await recognudges.nudgeClear(message)
                await channel.send(embed = embed)
                return
            
            # PERFORM SEARCH ON QUERY
            if (len(messageInfo["mentions"]["userMentions"]) == 0):
                sql = "SELECT authorid, content, receiverid, insultid FROM insults WHERE guildid = %s AND content ILIKE %s"
                val = (message.guild.id, str("%" + messageInfo["quotes"][0]["quote"] + "%"))
                cursor.execute(sql, val, )
                searchResults = cursor.fetchall()
            else:
                sql = "SELECT authorid, content, receiverid, insultid FROM insults WHERE guildid = %s AND authorid = %s"
                val = (message.guild.id, messageInfo["mentions"]["userMentions"][0].id)
                cursor.execute(sql, val, )
                searchResults = cursor.fetchall()
                
            # CHECK FOR RESULTS
            if (len(searchResults) == 0):
                
                # SEND ERROR EMBED
                embed = discord.Embed (
                    title = "No Results",
                    color = embedColor,
                    description = "I couldn't find anything with that search term."
                )
                
                embed.set_footer(text = "Try using a less specific search term")
                
                await recognudges.nudgeClear(message)
                await channel.send(embed = embed)
                return
                
            # AGGREGATE DATA  
            chunkID = 0
            searchChunks = [searchResults[x:x+5] for x in range(0, len(searchResults), 5)]
            
            await recognudges.nudgeClear(message)
            searchMessage = await channel.send("```> Search results Loading...```")
            
            # GENERATE EMBED
            contLoop = True
            while(contLoop == True):
                embed = discord.Embed (
                    title = str(
                        "Search Results | Page " + str(chunkID + 1) + " of " + str(len(searchChunks))
                    ),
                    color = embedColor
                )

                embed.set_footer(text = "Use the reactions to select items or change pages")

                for iteration, chunk in enumerate(searchChunks[chunkID]):
                    # COLLECT DATA
                    iA = client.get_user(chunk[0])                
                    iR = client.get_user(chunk[2])
                    if (iA == None):
                        insultAuthor = "A fallen member..."
                    else:
                        insultAuthor = "@" + iA.display_name

                    if (iR == None):
                        embed.add_field(
                            name = str(numberEmojis[iteration] + " " + chunk[1]),
                            value = str("Added by " + insultAuthor), 
                            inline = False
                        )
                    else:
                        embed.add_field(
                            name = str(numberEmojis[iteration] + " " + chunk[1]),
                            value = str("Added by " + insultAuthor + " for @" + iR.display_name), 
                            inline = False
                        )

                await searchMessage.edit(embed = embed, content = None)

                # ADD REACTIONS
                await searchMessage.clear_reactions()

                if (chunkID != 0):
                    await searchMessage.add_reaction("⬅️")

                for iteration, chunk in enumerate(searchChunks[chunkID]):
                    await searchMessage.add_reaction(numberEmojis[iteration])

                if (chunkID != len(searchChunks) - 1):
                    await searchMessage.add_reaction("➡️")

                # AWAIT A REACTION
                def check(reaction, member):
                    return reaction and member == message.author

                try: 
                    reaction, member = await client.wait_for("reaction_add", timeout = 60.0, check = check)
                except asyncio.TimeoutError:
                    await searchMessage.clear_reactions()
                    return

                # CHECK REACTION
                if (str(reaction.emoji) == "⬅️"):
                    chunkID -= 1
                    continue
                elif (str(reaction.emoji) == "➡️"):
                    chunkID += 1
                    continue
                
                for iteration, emoji in enumerate(numberEmojis): 
                    if (str(reaction.emoji) == emoji):
                        selectedInsultID = iteration
                        contLoop = False
                        break
                        
                        
            # GENERATE FOCUSED INSULT VIEW
            selectedInsult = searchChunks[chunkID][selectedInsultID]
            iA = client.get_user(selectedInsult[0])                
            iR = client.get_user(selectedInsult[2])
            if (iA == None):
                insultAuthor = "A fallen member..."
            else:
                insultAuthor = "@" + iA.display_name
            
            embed = discord.Embed (
                title = selectedInsult[1],
                color = embedColor
            )
            
            if (iR == None):
                embed.set_footer(text = str("Added by " + insultAuthor))
            else:
                embed.set_footer(text = str("Added by " + insultAuthor + " for @" + iR.display_name))

                
            # UPDATE EMBED
            await searchMessage.edit(embed = embed)
            
            # ADD REACTIONS
            await searchMessage.clear_reactions()
            await searchMessage.add_reaction("🗑️")
            #await searchMessage.add_reaction("✏️")
            
            # AWAIT A REACTION
            def check(reaction, member):
                    return reaction and member == message.author

            try: 
                reaction, member = await client.wait_for("reaction_add", timeout = 60.0, check = check)
            except asyncio.TimeoutError:
                await searchMessage.clear_reactions()
                return
            
            # CHECK REACTION
            if (str(reaction.emoji) == "🗑️"):
                
                # DELETE INSULT
                sql = "DELETE FROM insults WHERE insultid = %s"
                val = (selectedInsult[3], )
                cursor.execute(sql, val)
                conn.commit()
                
                # RETURN EMBED
                embed = discord.Embed (
                    title = selectedInsult[1],
                    color = embedColor
                )
                embed.set_footer(text = "Deleted")
                
                await searchMessage.edit(embed = embed)
                await searchMessage.clear_reactions()

            return

            

        elif ("COOLDOWN" in sentence or "DELAY" in sentence):
    
            # FETCH PERMISSIONS
            adminPrivilleges = adminverify.verify(author)

            # CHECK PERMISSIONS
            if (adminPrivilleges[0] == False):

                    # SEND ERROR EMBED
                    embed = discord.Embed ( 
                        title = "Invalid Permisssions",
                        color = embedColor,
                        description = str(
                            '''You do not have permission to use this command at the moment. You must be a **Moderator** or **Administrator** to do so.'''
                        )
                    )

                    await recognudges.nudgeClear(message)
                    await channel.send(embed = embed)
                    return

            # GET GUILD INFO
            sql = "SELECT insultcooldown FROM guildinfo WHERE id = %s"
            val = (message.guild.id, )
            cursor.execute(sql, val)
            insultcooldown = cursor.fetchone()[0]

            # CREATE COOLDOWN EMBED
            embed = discord.Embed (
                title = "Updating the Insult Cooldown",
                color = embedColor,
                description = str(
                    '''This server's current cooldown is **''' + str(insultcooldown) + '''m**.'''
                )
            )

            embed.set_footer(text = "Select a new cooldown with the reactions")

            embed.add_field (
                name = str('''**COOLDOWN OPTIONS**'''), 
                value = str(
                    numberEmojis[0] + ''' 1 Minute \n''' +
                    numberEmojis[1] + ''' 2 Minutes \n''' +
                    numberEmojis[2] + ''' 3 Minutes \n''' +
                    numberEmojis[3] + ''' 4 Minutes \n''' +
                    numberEmojis[4] + ''' 5 Minutes \n''' +
                    '''❗ **No Cooldown (Dangerous)**'''
                )
            )

            await recognudges.nudgeClear(message)
            embedMessage = await channel.send(embed = embed)

            # ADD REACTIONS
            await embedMessage.clear_reactions()

            for emoji in numberEmojis:
                await embedMessage.add_reaction(emoji)
            
            await embedMessage.add_reaction("❗")

            # AWAIT REACTION
            def check(reaction, member):
                return reaction and member == message.author

            try:
                reaction, member = await client.wait_for("reaction_add", timeout = 60.0, check = check)
            except asyncio.TimeoutError:
                await embedMessage.clear_reactions()
                return

            # CHECK REACTION
            newCooldown = 0
            for iteration, emoji in enumerate(numberEmojis):
                if (str(reaction.emoji) == emoji):
                    newCooldown = iteration + 1
                    break
            
            # UPDATE DATABASE
            sql = "UPDATE guildinfo SET insultcooldown = %s WHERE id = %s"
            val = (newCooldown, message.guild.id, )
            cursor.execute(sql, val)
            conn.commit()

            # UPDATE EMBED
            await embedMessage.clear_reactions()

            embed = discord.Embed (
                title = "Updated Insult Cooldown", 
                color = embedColor, 
                description = str( 
                    "This server's new cooldown is **" + str(newCooldown) + "m!**"
                )
            )

            await embedMessage.edit(embed = embed)
            return



                


        
    elif (subject == "TARGET" or subject == "TARGETING" or subject == "TARGETTING"):
        
        # FETCH PERMISSIONS
        adminPrivilleges = adminverify.verify(author)

        if ("DISABLE" in sentence or "DISABLED" in sentence or "OFF" in sentence):

            # CHECK PERMISSIONS
            if (adminPrivilleges[0] == False):

                # SEND AN ERROR EMBED
                embed = discord.Embed (
                    title = "Invalid Permissions",
                    color = embedColor,
                    description = str(
                        '''You do not have permission to use this command. You must be a **Moderator** or **Administrator** to do so.'''
                    )
                )

                await recognudges.nudgeClear(message)
                await channel.send(embed = embed)
                return

            # CHECK DATABASE
            sql = "SELECT targeteduserid FROM guildinfo WHERE id = %s"
            val = (message.guild.id, )
            cursor.execute(sql, val)
            targetedUserID = cursor.fetchone()

            if (targetedUserID == 0):

                # SEND A MESSAGE EMBED
                embed = discord.Embed (
                    title = "Nobody's Targeted",
                    color = embedColor, 
                    description = str(
                        '''You doing alright? Nobody's targeted at the moment.'''
                    )
                )

                await recognudges.nudgeClear(message)
                await channel.send(embed = embed)
                return

            # UPDATE DATABASE
            sql = "UPDATE guildinfo SET targeteduserid = 0 WHERE id = %s"
            val = (message.guild.id, )
            cursor.execute(sql, val)
            conn.commit()

            # SEND SUCCESS EMBED
            embed = discord.Embed (
                title = "Disabled Insult Targeting",
                color = embedColor,
                description = str(
                    '''Nobody's targeted anymore, and only moderators can target people for now.'''
                )
            )

            embed.set_footer(text = "Wow, you're boring")

            await recognudges.nudgeClear(message)
            await channel.send(embed = embed)
            return



        # CHECK FOR MENTIONS
        elif (len(messageInfo["mentions"]["userMentions"]) == 0):
            
            # SEND ERROR EMBED
            if (message.mention_everyone == True):
                
                # SEND ERROR EMBED
                embed = discord.Embed ( 
                    title = "I Can't Target Everything",
                    color = embedColor,
                    description = str(
                        "Calm down there, old sport. Targeting everyone would just be downright annoying."
                    )
                )
                
            else:
            
                # SEND ERROR EMBED
                embed = discord.Embed ( 
                    title = "I Can't Target Nothing",
                    color = embedColor,
                    description = str(
                        "The void doesn't respond to insults as well as people."
                    )
                )
                
            embed.set_footer(text = "Try @mentioning someone next time")
            
            await recognudges.nudgeClear(message)
            await channel.send(embed = embed)
            return
        
        elif (len(messageInfo["mentions"]["userMentions"]) > 1):
            
            # SEND ERROR EMBED
            embed = discord.Embed ( 
                title = "I Can't Target Everyone",
                color = embedColor,
                description = str(
                    "Whoa there, buddy. Try mentioning just one person next time; too many and I have no idea what you're on about."
                )
            )
            
            await recognudges.nudgeClear(message)
            await channel.send(embed = embed)
            return
        
        mentionedMember = messageInfo["mentions"]["userMentions"][0]
        
        
        # CHECK FOR SELF MENTIONS
        if (mentionedMember.id == client.user.id):
            
            # SEND ERROR EMBED
            embed = discord.Embed ( 
                title = "I'm Not Targetting Myself",
                color = embedColor,
                description = str(
                    "You thought you could cheese the system and spam the channels. If only I was that stupid."
                )
            )
            
            embed.set_footer(text = "Nice try, though")
            
            await recognudges.nudgeClear(message)
            await channel.send(embed = embed)
            return
        
        # CHECK CURRENT TARGET & PERMISSIONS
        sql = "SELECT targeteduserid FROM guildinfo WHERE id = %s"
        val = (message.guild.id, )
        cursor.execute(sql, val)
        targetedUserID = cursor.fetchone()

        if (targetedUserID == 0 and adminPrivilleges == 0):

            # SEND AN ERROR EMBED
            embed = discord.Embed ( 
                title = "Invalid Permissions",
                color = embedColor,
                description = str(
                    '''You do not have permission to use this command at the moment. You must be a **Moderator** or **Administrator** to enable targeting.'''
                )
            )
            
            await recognudges.nudgeClear(message)
            await channel.send(embed = embed)
            return
        
        # UPDATE DATABASE
        sql = "UPDATE guildinfo SET targeteduserid = %s WHERE id = %s"
        val = (mentionedMember.id, message.guild.id, )
        cursor.execute(sql, val)
        conn.commit()
        
        # SEND SUCCESS EMBED
        embed = discord.Embed (
            title = str("Beware @" + mentionedMember.display_name + "!"),
            color = embedColor,
            description = str(
                "You have been targeted! Our battle will be glorious!"
            )
        )
        
        await recognudges.nudgeClear(message)
        await channel.send(embed = embed)
        return
    
    await recognudges.nudgeConfused(message)   