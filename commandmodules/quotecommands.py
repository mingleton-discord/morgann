# QUOTE COMMANDS

# Handles commands for quotes

# IMPORT MODULES
import discord
import psycopg2
import random
import asyncio
from modules import adminverify, recognudges


# VARIABLES
moduleVersion = 2.0
triggerWords = ["QUOTE"]
numberEmojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]


# INITALIZE
def initialize(c, co):
    
    # DEBUG
    print("> Initializing Module: Quote Commands")
    
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
        "name" : "Quote Commands", 
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
    if (subject == "QUOTE"):
        
        # CHECK FOR TOPIC
        if ("ADD" in sentence):                 # ADD A QUOTE
            
            # FIND THE QUOTE
            quote = ""
            for quote in messageInfo["quotes"]:
                if (quote["sentID"] == sentID):
                    quote = quote["quote"].capitalize()
                    break
            else:
                
                # SEND AN ERROR EMBED
                embed = discord.Embed (
                    title = "No Quote Found",
                    color = embedColor,
                    description = str(
                        '''Try using `"` around your quote. For example, `"You're trash at quoting people"`'''
                    )
                )
                
                await recognudges.nudgeClear(message)
                await channel.send(embed = embed)
                return
            
            # CHECK IF SOMEONE IS QUOTED
            quoteAuthorID = 0
            if (len(messageInfo["mentions"]["userMentions"]) > 0):
                
                quoteAuthorID = messageInfo["mentions"]["userMentions"][0].id
                
                # ADD TO DB
                sql = "INSERT INTO quotes (quoteid, guildid, creatorid, version, content, authorid) VALUES (%s, %s, %s, %s, %s, %s)"
                val = (message.id, message.guild.id, author.id, moduleVersion, quote, quoteAuthorID)
                cursor.execute(sql, val)
                conn.commit()
                
                # SEND SUCCESS EMBED
                embed = discord.Embed (
                    title = str(
                        '"' + quote + '"'
                    ),
                    color = embedColor
                )
                
                embed.set_footer(text = str(
                    "- @" + messageInfo["mentions"]["userMentions"][0].display_name + 
                    " | Added"
                ))
                
                await recognudges.nudgeClear(message)
                await channel.send(embed = embed)
                return
                

            # ASK FOR A QUOTER
            embed = discord.Embed (
                title = "No Author Found",
                color = embedColor,
                description = str(
                    "Respond to this message with the name of the person this is from"
                )
            )
            
            questionMessage = embed.set_footer(text = "This will timeout in 60 seconds")
            
            await recognudges.nudgeClear(message)
            await channel.send(embed = embed)
            
            def check(m):
                return m.channel == channel
            
            try:
                responseMessage = await client.wait_for("message", timeout = 60.0, check = check)
            except asyncio.TimeoutError:
                
                # SEND ERROR EMBED
                embed = discord.Embed (
                    title = "No Response Given",
                    color = embedColor,
                    description = str(
                        "It looks like you didn't give a response in time!"
                    )
                )
                
                embed.set_footer(text = "Please try again")
                await questionMessage.edit(embed = embed)
                return
            
            # ADD TO DB
            sql = "INSERT INTO quotes (quoteid, guildid, creatorid, version, content, authorname) VALUES (%s, %s, %s, %s, %s, %s)"
            val = (message.id, message.guild.id, author.id, moduleVersion, quote, responseMessage.clean_content)
            cursor.execute(sql, val)
            conn.commit()
            
            # SEND SUCCESS EMBED
            embed = discord.Embed (
                title = str(
                    '"' + quote + '"'
                ),
                color = embedColor
            )

            embed.set_footer(text = str(
                "- " + responseMessage.clean_content + 
                " | Added"
            ))

            await recognudges.nudgeClear(message)
            await channel.send(embed = embed)
            return
            
        
        
        elif ("RANDOM" in sentence):                 # SELECT RANDOM QUOTE
            
            # GET ALL QUOTES
            sql = "SELECT creatorid, content, authorname, authorid FROM quotes WHERE guildid = %s"
            val = (message.guild.id, )
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
            
            await recognudges.nudgeClear(message)
            await channel.send(embed = embed)
            return
            
        
        
        elif ("DAILY" in sentence and "SETUP" in sentence):       # SETUP DAILY QUOTES
            
            # CHECK PERMISSIONS
            adminPrivilleges = adminverify.verify(author)

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

            # GET ALL QUOTES
            sql = "SELECT creatorid, content, authorname, authorid FROM quotes WHERE guildid = %s"
            val = (message.guild.id, )
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
            
            await recognudges.nudgeClear(message)
            quoteMessage = await channel.send(embed = embed)
            
            # SAVE MESSAGE INFORMATION
            sql = "UPDATE guildinfo SET dqchannelid = %s, dqmessageid = %s WHERE id = %s"
            val = (quoteMessage.channel.id, quoteMessage.id, quoteMessage.guild.id)
            cursor.execute(sql, val)
            conn.commit()
            
            # SEND ANOTHER MESSAGE
            await channel.send("> You can pin the message above. It will update every day with a new, random quote.")
            return
            
        
        
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
                sql = "SELECT creatorid, content, authorname, authorid, quoteid FROM quotes WHERE guildid = %s AND content ILIKE %s"
                val = (message.guild.id, str("%" + messageInfo["quotes"][0]["quote"] + "%s"))
                cursor.execute(sql, val)
                searchResults = cursor.fetchall()
            else:
                sql = "SELECT creatorid, content, authorname, authorid, quoteid FROM quotes WHERE guildid = %s AND creatorid = %s OR authorid = %s"
                val = (message.guild.id, messageInfo["mentions"]["userMentions"][0].id, messageInfo["mentions"]["userMentions"][0].id)
                cursor.execute(sql, val)
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
            searchMessage = await channel.send("```> Search Results Loading...```")
            
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
                    qC = client.get_user(chunk[0])
                    qA = client.get_user(chunk[3])
                    
                    if (qC == None):
                        quoteCreator = "A fallen member..."
                    else:
                        quoteCreator = "@ " + qC.display_name
                        
                    if (qA == None):
                        quoteAuthor = chunk[2]
                    else:
                        quoteAuthor = "@ " + qA.display_name
                        
                    embed.add_field (
                        name = str(numberEmojis[iteration] + ' "' + chunk[1] + '"'),
                        value = str("- " + quoteAuthor + " | Added by " + quoteCreator),
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
                        selectedQuoteID = iteration
                        contLoop = False
                        break
                        
                        
                # GENERATE FOCUSED QUOTE VIEW
                selectedQuote = searchChunks[chunkID][selectedQuoteID]
                qC = client.get_user(chunk[0])
                qA = client.get_user(chunk[3])

                if (qC == None):
                    quoteCreator = "A fallen member..."
                else:
                    quoteCreator = "@ " + qC.display_name

                if (qA == None):
                    quoteAuthor = chunk[2]
                else:
                    quoteAuthor = "@ " + qA.display_name
                    
                embed = discord.Embed (
                    title = str('"' + selectedQuote[1] + '"'),
                    color = embedColor
                )
                embed.set_footer(text = str("- " + quoteAuthor + " | Added by " + quoteCreator))
                
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
                    sql = "DELETE FROM quotes WHERE quoteid = %s"
                    val = (selectedQuote[3], )
                    cursor.execute(sql, val)
                    conn.commit()

                    # RETURN EMBED
                    embed = discord.Embed (
                        title = selectedQuote[1],
                        color = embedColor
                    )
                    embed.set_footer(text = "Deleted")

                    await searchMessage.edit(embed = embed)
                    await searchMessage.clear_reactions()  

            return

    await recognudges.nudgeConfused(message) 
            
            
            