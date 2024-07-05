from http import server
from logging import exception
from sqlite3 import Timestamp
from turtle import title
import discord
import random
from discord.ext import commands
import asyncio
import json
from discord.user import User
from discord import Embed
import aiofiles
import os
from webserver import keep_alive
from asyncio import sleep as s


intents = discord.Intents.default()
intents.members = True
intents=discord.Intents().all()
client=commands.Bot(command_prefix='.', intents=intents)
client.warnings= {} # guild_id : {member_id: [count, [(admin_id, reason)]]}
client.reaction_roles = []


@client.command()
async def reminder(ctx, time: int, *, msg):
  if (not ctx.author.guild_permissions.manage_messages):
    await ctx.send('This command requires Manage Messages')
    return

  while True:
    await s(3600*time)
    await ctx.send(f'{msg}')





@client.event
async def on_ready():
    for guild in client.guilds:
        client.warnings[guild.id] = {}

        async with aiofiles.open(f"{guild.id}.txt", mode="a") as temp:
            pass

        async with aiofiles.open(f"{guild.id}.txt", mode="r") as file:
            lines = await file.readlines()

            for line in lines:
                data = line.split(" ")
                member_id = int(data[0])
                admin_id = int(data[1])
                reason = " ".join(data[2:]).strip("\n")

                try:
                    client.warnings[guild.id][member_id][0] += 1
                    client.warnings[guild.id][member_id][1].append((admin_id, reason))

                except KeyError:
                    client.warnings[guild.id][member_id] = [1, [(admin_id, reason)]] 



@client.event
async def on_guild_join(guild):
    client.warnings[guild.id] = {}

@client.command()
@commands.has_permissions(administrator=True)
async def warn(ctx, member: discord.Member=None, *, reason=None):
    if member is None:
        return await ctx.send("The provided member could not be found or you forgot to provide one.")

    if reason is None:
        return await ctx.send("Please provide a reason for warning this user.")

    try:
        first_warning = False
        client.warnings[ctx.guild.id][member.id][0] += 1
        client.warnings[ctx.guild.id][member.id][1].append((ctx.author.id, reason))

    except KeyError:
        first_warning = True
        client.warnings[ctx.guild.id][member.id] = [1, [(ctx.author.id, reason)]]

    count = client.warnings[ctx.guild.id][member.id][0]

    async with aiofiles.open(f"{ctx.guild.id}.txt", mode="a") as file:
        await file.write(f"{member.id} {ctx.author.id} {reason}\n")

    await ctx.send(f"{member.mention} has {count} {'warning' if first_warning else 'warnings'}.")

@client.command()
@commands.has_permissions(administrator=True)
async def warnings(ctx, member: discord.Member=None):
    if member is None:
        return await ctx.send("The provided member could not be found or you forgot to provide one.")

    embed = discord.Embed(title=f"Displaying Warnings for {member.name}", description="", colour=discord.Colour.red())
    try:
        i = 1
        for admin_id, reason in client.warnings[ctx.guild.id][member.id][1]:
            admin = ctx.guild.get_member(admin_id)
            embed.description += f"**Warning {i}** given by: {admin.mention} for: *'{reason}'*.\n"
            i += 1

        await ctx.send(embed=embed)

    except KeyError: # no warnings
        await ctx.send("This user has no warnings.")

@client.event
async def on_ready():
    async with aiofiles.open("reaction_roles.txt", mode="a") as temp:
        pass
        
    async with aiofiles.open("reaction_roles.txt", mode="r") as file:
        lines = await file.readlines()
        for line in lines:
            data = line.split(" ")
            client.reaction_roles.append((int(data[0]), int(data[1]), data[2].strip("\n")))

   

@client.command()
async def set_reaction(ctx, role: discord.Role=None, msg: discord.Message=None, emoji=None):
    if role != None and msg != None and emoji != None:
        await msg.add_reaction(emoji)
        client.reaction_roles.append((role.id, msg.id, str(emoji.encode("utf-8"))))
        
        async with aiofiles.open("reaction_roles.txt", mode="a") as file:
            emoji_utf = emoji.encode("utf-8")
            await file.write(f"{role.id} {msg.id} {emoji_utf}\n")

        await ctx.channel.send("Reaction has been set.")
        
    else:
        await ctx.send("Invalid arguments.")

@client.event
async def on_raw_reaction_add(payload):
    for role_id, msg_id, emoji in client.reaction_roles:
        if msg_id == payload.message_id and emoji == str(payload.emoji.name.encode("utf-8")):
            await payload.member.add_roles(client.get_guild(payload.guild_id).get_role(role_id))
            return

@client.event
async def on_raw_reaction_remove(payload):
    for role_id, msg_id, emoji in client.reaction_roles:
        if msg_id == payload.message_id and emoji == str(payload.emoji.name.encode("utf-8")):
            guild = client.get_guild(payload.guild_id)
            await guild.get_member(payload.user_id).remove_roles(guild.get_role(role_id))
            return








@client.command()
@commands.has_role('👑Staff')
async def dm(ctx, user_id=None, *, args=None):
    if user_id != None and args != None:
        try:
            target = await client.fetch_user(user_id)
            await target.send(args)

            await ctx.channel.send("'" + args + "' sent to: " + target.name)

        except:
            await ctx.channel.send("Couldn't dm the given user.")
        

    else:
        await ctx.channel.send("You didn't provide a user's id and/or a message.")

@client.command()
@commands.has_role('Owner  [Adm]💎')
async def dm_all(ctx, *, args=None):
  if args != None:
    members = ctx.guild.members
    for member in members:
      try:
        await member.send(args)
        print("'" + args + "' sent to:" + member.name)
      
      except:
        print('Couldnt send ' + args + "' to " + member.name)

  else:
    await ctx.channel.send("You dindt provide arguments.")


@client.event
async def on_ready():
  await client.change_presence(status=discord.Status.idle, activity=discord.Game('Genshin Impact'))
  print('El bot esta listo.')



@client.command()
@commands.has_role('👑Staff')
async def ban(ctx, member : discord.Member, *,   reason=None):
  await member.ban(reason=reason)
  await ctx.send(f'{member.mention} Fue Baneado de Celestia Realm (•̀o•́)ง')
  await member.send(f'Has sido baneado en el server {guild.name} por la razón: {reason}')
  






@client.command()
@commands.has_role('👑Staff')
async def unban(ctx, *, member):
  banned_users = await ctx.guild.bans()
  member_name, member_discriminator = member.split('#')

  for ban_entry in banned_users:
    user = ban_entry.user

    if(user.name, user.discriminator) == (member_name, member_discriminator):
      await ctx.guild.unban(user)
      await ctx.send(f'{user.mention} Fue desbaneado espero que se comporte ಠ_ಠ')
      return
  
@client.event
async def on_command_error(ctx, error):
  if isinstance(error, commands.CommandNotFound):
    await ctx.send('(╯°□°）╯ ¿Buscas pelea? ese comando no existe!')





@client.command()
@commands.has_role('👑Staff')
async def clear(ctx,amount : int):
  await ctx.channel.purge(limit=amount)
  
@clear.error
async def clear_error(ctx, error):
  if isinstance(error, commands.MissingRequiredArgument):
    await ctx.send('Porfavor especifica la cantidad de mensajes que quieres borrar melon ಠ_ಠ')


punch_gifs = ['https://c.tenor.com/p_mMicg1pgUAAAAC/anya-forger-damian-spy-x-family.gif','https://c.tenor.com/iMdhHUe87loAAAAd/genos-one-punch-man.gif']
punch_names = ["Te ha golpeado!"]


@client.command()
async def punch(ctx):
  embed = discord.Embed(colour=(discord.Colour.random()), description=f"{ctx.author.mention} {(random.choice(punch_names))}")
  embed.set_image(url=(random.choice(punch_gifs)))
  await ctx.send(embed=embed)

kiss_gifs = ['https://c.tenor.com/O1-IX-P5ugQAAAAd/koi-to-uso-anime.gif', 'https://c.tenor.com/sDOs4aMXC6gAAAAd/anime-sexy-kiss-anime-girl.gif', 'https://c.tenor.com/qJn0BvtQ4ZUAAAAd/hey-anime.gif', 'https://cdn.discordapp.com/attachments/971128433327345664/982227732798783518/IMG_0313.gif', 'https://cdn.discordapp.com/attachments/971128433327345664/982228221070278666/IMG_0314.gif']

kiss_names = ["Te ha besado!"]

@client.command()
async def kiss(ctx):
  embed = discord.Embed(colour=(discord.Colour.random()), description=f"{ctx.author.mention} {(random.choice(kiss_names))}")
  embed.set_image(url=(random.choice(kiss_gifs)))
  await ctx.send(embed=embed)

@client.command()
@commands.has_role('👑Staff')
async def getembed(ctx, *, content):
  embed = discord.Embed(title="", description=f"{content}")
  
  await ctx.message.delete()
  await ctx.send(embed=embed)


@client.command()
@commands.has_role('👑Staff')
async def getembed2(ctx, *, content):
  embed = discord.Embed(title="", description=f"{content}")
  
  channel = client.get_channel(985952162087600139)
  await channel.send(embed=embed)

@client.command()
@commands.has_role('Owner  [Adm]💎')
async def say(ctx, *, message):
  await ctx.message.delete()
  await ctx.send(f"{message}" .format(message))
  
@client.command()
@commands.has_role('Owner  [Adm]💎')
async def say2(ctx, *, message):
  await ctx.message.delete()
  channel = client.get_channel(940622189399527524)
  await channel.send(f"{message}" .format(message)) 






@client.command(description='Silencias al usuario especificado')
@commands.has_permissions(manage_messages=True)
@commands.has_role('👑Staff')
async def mute(ctx, member: discord.Member, *, reason=None):
  guild = ctx.guild
  mutedRole = discord.utils.get(guild.roles, name='Muted')

  if not mutedRole:
    mutedRole = await guild.create_role(name='Muted')

    for channel in guild.channels:
      await channel.set_permissions(mutedRole, speak=False, send_messages=False, read_message_history=True, read_messages=False)

  await member.add_roles(mutedRole, reason=reason)
  await ctx.send(f'{member.mention} Ha sido silenciado por la razón: {reason}')
  await member.send(f'Has sido silenciado en el server {guild.name} por la razón: {reason}')


@client.command(description= 'Desmutea al usuario especificado')
@commands.has_permissions(manage_messages=True)
@commands.has_role('👑Staff')
async def unmute(ctx, member: discord.Member):
  mutedRole = discord.utils.get(ctx.guild.roles, name='Muted')

  await member.remove_roles(mutedRole)
  await ctx.send(f'{member.mention} has sido desmuteado')
  await member.send(f'Has sido desmuteado del server {guild.name} por la razón: {reason}')

@client.command(name="whois")
async def whois(ctx,user:discord.Member=None):

  if user==None:
    user=ctx.author

  rlist = []
  for role in user.roles:
    if role.name != '@everyone':
      rlist.append(role.mention)
  
  b = ','.join(rlist)  



  embed = discord.Embed(colour=user.color,Timestamp=ctx.message.created_at)

  embed.set_author(name=f'User Info - {user}'),
  embed.set_thumbnail(url=user.avatar_url),
  embed.set_footer(text=f'Requested by - {ctx.author}',
  icon_url=ctx.author.avatar_url)

  embed.add_field(name='ID:',value=user.id,inline=False)
  embed.add_field(name='Name:',value=user.display_name,inline=False)

  embed.add_field(name='Created at:',value=user.created_at,inline=False)
  embed.add_field(name='Joined at:',value=user.joined_at,inline=False)

  embed.add_field(name='Bot?',value=user.bot,inline=False)

  embed.add_field(name=f'Roles:({len(rlist)})',value=''.join([b]),inline=False)
  embed.add_field(name='Top Role:',value=user.top_role.mention,inline=False)

  await ctx.send(embed=embed)


@client.command()
async def slowmode(ctx,time:int):
  if (not ctx.author.guild_permissions.manage_messages):
    await ctx.send('This command requires Manage Messages')
    return
  try:
    if time == 0:
      await ctx.send('Slowmode Off')
      await ctx.channel.edit(slowmode_delay = 0)
    elif time > 21600:
      await ctx.send('You can not set the slowmode above 6 hours')
      return
    else:
      await ctx.channel.edit(slowmode_delay = time)
      await ctx.send(f'Slowmode set to {time} seconds!')
  except Exception:
    await print('Oops!')


@client.command()
async def serverinfo(ctx):
  role_count = len(ctx.guild.roles)
  list_of_bots = [bot.mention for bot in ctx.guild.members if bot.bot]

  serverinfoEmbed = discord.Embed(timestamp=ctx.message.created_at, color=ctx.author.color)
  serverinfoEmbed.add_field(name='Name',value=f'{ctx.guild.name}',inline=False)
  serverinfoEmbed.add_field(name='Member Count',value=ctx.guild.member_count,inline=False)
  serverinfoEmbed.add_field(name='Verification Level',value=str(ctx.guild.verification_level),inline=False)
  serverinfoEmbed.add_field(name='Highest Role',value=ctx.guild.roles[-2],inline=False)
  serverinfoEmbed.add_field(name='Number of Roles',value=str(role_count),inline=False)
  serverinfoEmbed.add_field(name='Bots',value=','.join(list_of_bots),inline=False)
  serverinfoEmbed.add_field(name='Name',value=f'{ctx.guild.name}',inline=False)
  

  await ctx.send(embed=serverinfoEmbed)



@client.event
async def on_message_delete (message):
    print("Borrado")
    embed = Embed(title=f"❌ {message.author.name} ha borrado un mensaje ❌")
    embed.add_field(name="Mensaje borrado", value=f"{message.content}", inline=False)
    channel = client.get_channel(985563757029777427)
    await channel.send(embed=embed)


@client.event
async def on_message_edit(message_before, message_after):
    print("Editando")
    embed = Embed(title=f"⚠️ {message_before.author.name} ha editado un mensaje ⚠️")
    embed.add_field(name="Mensaje anterior", value=f"{message_before.content}", inline=False)
    embed.add_field(name="Mensaje editado", value=f"{message_after.content}", inline=False)
    channel = client.get_channel(985563757029777427)
    await channel.send(embed=embed)





@client.event
async def on_guild_join(guild):
  with open('prefixes.json','r') as f:
    prefixes=json.load(f)

  prefixes[str(guild.id)]= 'c!'

  with open('prefixes.json', 'w') as f:
    json.dump(prefixes, f, indent=4)


@client.event
async def on_member_join(member):
  channel1 = client.get_channel(940618388986814504)
  channel2 = client.get_channel(985563168380157962)
  channel3 = client.get_channel(940617047929401394)
  welcomeEmbed=discord.Embed(title=f'Welcome to Celestia Realm ♡!', description=f'¡Ojo! Ha llegado {member.mention} al server', color=discord.Color.blue())
  welcomeEmbed.set_image(url='https://media.discordapp.net/attachments/962306199590694912/981679433930907678/yelan.gif')
  welcomeEmbed.add_field(name='════ ⋆★⋆ ════', value=f'Esperemos que pases momentos increíbles con nosotros, recuerda pasarte por {channel1.mention} para aprender un poquito sobre este reino y de paso ir a {channel2.mention} para que podamos saber un poquito más sobre tí (^^♪). En {channel3.mention} estaremos encantadísimos de darte la bienvenida, ¿Qué esperas? ¡Pásate! ', inline=False)
  
  await client.get_channel(940614157370273884).send(f"Welcome! {member.mention}")
  await client.get_channel(940614157370273884).send(embed=welcomeEmbed)
  




@client.event
async def on_guild_remove(guild):
  with open('prefixes.json', 'r') as f:
    prefixes=json.load(f)

  prefixes.pop(str(guild.id))

  with open('prefixes.json', 'w') as f:
    json.dump(prefixes, f, indent=4)
















keep_alive()
TOKEN = os.environ.get("DISCORD_BOT_SECRET")
my_secret = os.environ['DISCORD_BOT_SECRET']
client.run(TOKEN)
