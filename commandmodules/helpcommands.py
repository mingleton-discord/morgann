# HELP COMMANDS

# Handles help-related commands

# IMPORT MODULES
import discord
from modules import recognudges, adminverify

# VARIABLES
moduleVersion = 1.0
triggerWords = ["HELP", "INFO", "ABOUT", "MANUAL", "WHAT"]


# INITIALIZE
def initialize(c):
    
    # DEBUG
    print("> Initializing Module: Help Commands")
    
    # PASS IN VARIABLES
    global client
    client = c
    
# RETURN INFO
def getInfo():
    
    # CREATE VARIABLES
    information = {
        "name" : "Help Commands", 
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
    if (subject == "HELP" or subject == "INFO" or subject == "ABOUT" or subject == "MANUAL" or subject == "WHAT"):
        
        if ("NEW" in sentence):

            embed = discord.Embed (
                title = "What's New in 21w01a | Help",
                color = embedColor,
                description = str(
                    '''
                    The Become Human update dropped March 2021, and brought on a slew of new features for you to dig your sadistic hands into, as well as cleaning up and refining old ones.
                    '''
                ),
                url = "https://morgann.isaacshea.com/"
            )

            embed.set_footer(text = "Click to view in the web manual")

            embed.add_field(
                name = "**GENERAL**",
                value = str(
                    ''' 
                     • The Rosetta Message Processing system was introduced allowing for brand new, intelligent understanding of your messages 
                     • Excellent at storing and dispensing those amazing one-liners everyone quotes
                     • The web client is now completely redesigned, with a fresh new visual appearance
                    '''
                ), 
                inline = False
            )

            embed.add_field(
                name = "**INSULTS**",
                value = str(
                    ''' 
                     • Insults can now be personalised - @mentioning someone when adding an insult will ensure it only appears for that person
                     • Insults now have a far better picking system - server insults will be chosen from until someone has more than 5 personalised insults just for them, in which case only their insults will be used
                     • Searching for insults has been improved by a huge amount - searching will create a search engine-like interface to select insults. The same has been done for searching for quotes
                    '''
                ), 
                inline = False
            )

            embed.add_field(
                name = "**QUOTES**",
                value = str(
                    ''' 
                     • Message quoting has been dramatically improved - @mentioning someone as the quote’s author will dynamically save their name, so it will update when their nickname does
                     • Reacting to a message with  3 📌 emojis will automatically quote it
                     • A daily quote system - each day, a random quote will be selected and displayed on a message that can be pinned to any channel
                    '''
                ), 
                inline = False
            )

            embed.add_field(
                name = "**MODERATION**",
                value = str(
                    ''' 
                     • Moderation tools overall have been significantly improved as to reduce the chaos Morgann can inflict
                     •  There is now new criteria for assessing administrators or moderators - Administrators are defined by Discord (such as server owners), and Moderators are defined by Morgann. Both have different levels of access and control over how Morgann functions
                     • By default, Morgann will wait 1 minute between insults, and this can be customised or turned off entirely
                     • Morgann is now able to be bound to entire categories of channels, as well as individual channels
                     • When a moderator disables targeting of insults, only other moderators will be able to re-enable targeting. Insults will not be able to be added during this time as well
                    '''
                ), 
                inline = False
            )

            await recognudges.nudgeClear(message)
            await channel.send(embed = embed)
            return



        elif ("INSULT" in sentence or "INSULTS" in sentence):

            embed = discord.Embed (
                title = "Insults | Help",
                color = embedColor,
                description = str(
                    '''
                    Ruining someone’s day is at the core of what Morgann does, and here’s how you can harness this power for your agenda.
                    '''
                ),
                url = "https://morgann.isaacshea.com/"
            )

            embed.set_footer(text = "Click to view in the web manual")

            embed.add_field(
                name = "**TARGETING SOMEONE**",
                value = str(
                    ''' 
                    When someone is targeted, they’ll be roasted using a randomly chosen insult every minute if they send messages (the interval is changeable). Targeting someone is as simple as telling Morgann:

                    *Morgann, target @mention*

                    **A Moderator must target someone for the first time after Morgann has joined your server, or has been turned off.**
                    '''
                ), 
                inline = False
            )

            embed.add_field(
                name = "**ADDING INSULTS**",
                value = str(
                    ''' 
                    Targeting someone is no good without any insults to throw their way. To add an insult, use:

                    *Morgann, add the insult “[your insult here]”*
                    
                    And he’ll handle the rest. If you’d like to get a little more personal about your attacks, you can ask Morgann to add an insult for a specific person using:

                    *Morgann, add the insult “[your personalised insult here]” for @mention*

                   **If Morgann is not targeting anyone, only Moderators can add insults.**
                    '''
                ), 
                inline = False
            )

            embed.add_field(
                name = "**BROWSING INSULTS**",
                value = str(
                    ''' 
                    If you’d like to search for an insult, or find a random one, you can ask Morgann to do exactly that:

                    *Morgann, give me a random insult

                    Morgann, search for an insult by @mention
                    Morgann, search for an insult for @mention
                    Morgann, search for an insult that has “[query]”*

                    Each of the search queries, provided there are results, will return a search engine-like menu for you to browse through your precious insults.

                    **Moderators can also remove insults through this menu.**
                    '''
                ), 
                inline = False
            )

            if (adminPrivilleges[0] == True):

                embed.add_field(
                    name = "**INSULT COOLDOWN**",
                    value = str(
                        ''' 
                        *Moderator Feature*
                        The insult cooldown is the interval that Morgann will insult the targeted user at, whenever they are messaging. By default, it is once a minute, but you can access or update this interval using:

                        *Morgann, update the insult cooldown*

                        A menu with the cooldown options will then appear. You can even turn the cooldown off entirely, but we warn this may become spammy or destructive to normal conversation.
                        '''
                    ), 
                    inline = False
                )

                embed.add_field(
                    name = "**DISABLING TARGETING & INSULTS**",
                    value = str(
                        ''' 
                        *Moderator Feature*
                        If you find Morgann’s insult feature annoying, it can be disabled using:

                        *Morgann, disable targeting*

                        This will stop Morgann from targeting anyone, accepting requests on who to target (except from Moderators), and disable the ability for insults to be added (except for Moderators).
                        '''
                    ), 
                    inline = False
                )

            await recognudges.nudgeClear(message)
            await channel.send(embed = embed)
            return


        elif ("QUOTE" in sentence or "QUOTES" in sentence):

            embed = discord.Embed (
                title = "Quotes | Help",
                color = embedColor,
                description = str(
                    '''
                    Storing those bizarre one-liners your friends say has never been easier! Here’s how to make use of it.
                    '''
                ),
                url = "https://morgann.isaacshea.com/"
            )

            embed.set_footer(text = "Click to view in the web manual")

            embed.add_field(
                name = "**AUTOMATIC QUOTING**",
                value = str(
                    ''' 
                    If someone posts a particularly noteworthy message, adding 3 pin 📌 reactions to it will automatically quote the message, storing the message’s author and the message’s content.

                    **The message must have text content. Morgann cannot save images.**
                    '''
                ), 
                inline = False
            )

            embed.add_field(
                name = "**MANUAL QUOTING**",
                value = str(
                    ''' 
                    In most circumstances, you may want to write down a quote someone said, and save it. You can do so by saying:

                    *Morgann, add the quote “[your quote here]” by @mention*
                    OR
                    *Morgann, add the quote “[your quote here]”*

                    If you chose the latter technique, you’ll have to respond to Morgann’s message with the author’s name within 60 seconds for it to save.
                    '''
                ), 
                inline = False
            )

            embed.add_field(
                name = "**BROWSING QUOTES**",
                value = str(
                    ''' 
                    Just as with insults, quotes can be searched for or randomly selected using the following commands: 

                    *Morgann, give me a random quote

                    Morgann, search for a quote by @mention
                    Morgann, search for a quote that has “[query]”*

                    Each of the search queries, provided there are results, will return a search engine-like menu for you to browse through your infamous quotes

                    **Moderators can also remove quotes through this menu.**
                    '''
                ), 
                inline = False
            )

            if (adminPrivilleges[0] == True):

                embed.add_field(
                    name = "**DAILY QUOTE**",
                    value = str(
                        ''' 
                        *Moderator Feature*
                        Morgann can be set up to update a message every day with a random quote from your server. You can begin the setup using:

                        *Morgann, setup our daily quotes*
                        
                        A message containing a random quote will then be generated, and you are encouraged to pin this message to the channel so you can easily see your quotes.
                        '''
                    ), 
                    inline = False
                )

            await recognudges.nudgeClear(message)
            await channel.send(embed = embed)
            return


        
        elif ("MOD" in sentence or "MODERATION" in sentence or "MODERATOR" in sentence or "ADMIN" in sentence or "ADMINISTRATION" in sentence or "ADMINISTRATOR" in sentence):

            embed = discord.Embed (
                title = "Moderation | Help",
                color = embedColor,
                description = str(
                    '''
                    Morgann can be quite a destructive bot, and as such some features have been implemented to assist Moderators in configuring him to their likes.

                    **Only Moderators can change these values.**
                    '''
                ),
                url = "https://morgann.isaacshea.com/"
            )

            embed.set_footer(text = "Click to view in the web manual")

            embed.add_field(
                name = "**ABOUT ADMINISTRATORS & MODERATORS**",
                value = str(
                    ''' 
                    There is a slight difference between Administrators and Moderators. Administrators are a level of management defined by Discord, such as your server’s owner. Administrators are generally configured in `Server Settings > Roles > Advanced Permissions`. 
                    Moderators are defined by Administrators as a lower-level moderation team. This would generally match your server’s moderation team.
                    '''
                ), 
                inline = False
            )

            if (adminPrivilleges[0] == True and adminPrivilleges[1] > 1):

                embed.add_field(
                    name = "**CONFIGURING MODERATORS**",
                    value = str(
                        ''' 
                        *Administrator Feature*
                        To set up or update your server’s Moderators, use the following command;

                        *Morgann, set the Moderator role to @role-mention*

                        Everyone with that role, and everyone who appears higher on your role hierarchy than that role, will be given Moderator permissions. This will remain dynamic, so if someone is demoted from Moderator in the future, Morgann will honour this.
                        '''
                    ), 
                    inline = False
                )

            if (adminPrivilleges[0] == True):

                embed.add_field(
                    name = "**CHANNEL/CATEGORY BINDING**",
                    value = str(
                        ''' 
                        *Moderator Feature*
                        To avoid Morgann being able to post in every channel, channel and category binding has been added. You can define a channel or category for Morgann to bind to by using:

                        *Morgann, bind to this channel
                        Morgann, bind to #channel*
                        OR
                        *Morgann, bind to this category
                        Morgann, bind to #channel’s category*

                        As soon as this is completed, Morgann will not respond to commands, insult people, or otherwise cause chaos outside of the defined areas.
                        '''
                    ), 
                    inline = False
                )

            await recognudges.nudgeClear(message)
            await channel.send(embed = embed)
            return


        else:

            embed = discord.Embed (
                title = "Home | Help",
                color = embedColor,
                description = str(
                    '''
                    I’m Morgann, a bot created by Isaac Shea to socially abuse his friends. If you want peace and tranquility in your server, you’ve got the wrong bot. If you want to cause chaos in the form of unrelenting textual abuse, I’m your guy.
                    '''
                ),
                url = "https://morgann.isaacshea.com/"
            )
            
            embed.set_footer(text = "Click to view in the web manual")
            
            embed.add_field(
                name = "**WHAT I DO**",
                value = str(
                    '''
                     • A specialist at delivering scathing insults from your friends
                     • Excellent at storing and dispensing those amazing one-liners everyone quotes
                     • Brilliant at handing out awards to all the absolute chads who put pineapple on pizza (among other things). You know pineapple belongs there, stop denying it
                    '''
                ), 
                inline = False
            )

            embed.add_field(
                name = "**USING ROSETTA**",
                value = str(
                    '''
                    Rosetta is a brand-new form of communicating with bots that Morgann has pioneered since his inception. It is designed to allow for more semantic communication - that is, talking to Morgann should feel more like talking to another person than talking to a bot.

                    **That being said, there are some things to keep in mind:**
                     • Every message must contain the word “Morgann”, or @mention Morgann for him to detect it.
                     • Morgann will recognise Discord objects (@mentions, #channels, etc.), so be sure to properly format them. 
                     • Nested text chunks (such as quotes or insults) must be placed within “double quotations” so that Morgann can find them properly.\
                    '''
                ), 
                inline = False
            )
            
            await recognudges.nudgeClear(message)
            await channel.send(embed = embed)
            return

    await recognudges.nudgeConfused(message)