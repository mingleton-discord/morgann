# RECOGNITION NUDGES

# Handles any semantic recognition-based responses for intuition

# IMPORT MODULES
import discord

# VARIABLES
moduleVersion = 2.0

# INITIALIZE
def initialize():
    
    # DEBUG 
    print ("> Initializing Module: Recognition Nudge Manager")



async def nudgeAware(message):

    await message.clear_reactions()
    await message.add_reaction("👋")

async def nudgeThink(message):

    await message.clear_reactions()
    await message.add_reaction("🤔")

async def nudgeConfused(message):

    await message.clear_reactions()
    await message.add_reaction("❓")

async def nudgeClear(message):
    
    await message.clear_reactions()