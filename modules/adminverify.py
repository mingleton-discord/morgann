# ADMIN VERIFIER

# Checks a member object to see if it is a admin/moderator

# IMPORT MODULES
import discord
import psycopg2

# INITIALIZE
def initialize(co, cl):
    
    # DEBUG 
    print ("> Initializing Module: Admin Verifier")
    
    # INIT VARIABLES
    global conn
    global cursor
    global client
    
    conn = co
    cursor = conn.cursor()
    client = cl
    
    
def verify(member):
    
    # CHECK IF DISCORD-ADMIN
    if (member.guild_permissions.administrator == True):
        return((True, 2))
    
    # GET ADMIN ROLE POSITION
    sql = "SELECT modroleposition FROM guildinfo WHERE id = %s"
    val = (member.guild.id, )
    cursor.execute(sql, val)
    modRolePosition = cursor.fetchone()[0]
    
    # CHECK IF MEMBER IS ABOVE THE MODERATOR ROLE POSITION
    if (modRolePosition == 0):
        return((False, 0))
        
    if (member.top_role.position >= modRolePosition):
        return((True, 1))
    else:
        return((False, 0))