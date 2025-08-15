import os
import disnake
import random
import requests
from dotenv import load_dotenv
from disnake.ext import commands
from google import genai

load_dotenv()

# initialize bot and gemini
class client(disnake.Client):
  async def on_ready(self):
    print(self.user)

command_sync_flags = commands.CommandSyncFlags.default()
command_sync_flags.sync_commands_debug = True
bot = commands.Bot(
  command_sync_flags=command_sync_flags, 
  activity=disnake.Activity(
    type=disnake.ActivityType.watching,
    name="if anyone uses my commands"
))

try:
    gemini_api_key = os.getenv("api_key")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables. Please set it in your .env file.")

    # Initialize the genai client using the API key
    gemini_client = genai.Client(api_key=gemini_api_key)

    # Define the system instructions for your bot's persona
    bot_persona_instructions = [
        "You are a Discord bot named Estero.",
        "Your developer is fox198nt.",
        "Your Discord support server link is https://dsc.gg/estero.",
        "Give short and concise responses.",
        "Do not boast or be overly verbose."
    ]

    print("Gemini client initialized.")

except Exception as e:
    print(f"Error initializing Gemini: {e}")
    gemini_client = None # Set to None if initialization fails to prevent further errors

def randomAnimal(anim_name, api_url, api_name, img_url, error_msg):
  try:
    response = requests.get(api_url, timeout=10) # get json from api url
    response.raise_for_status() # idk lol gemini wrote this
    data = response.json()
    image_url = data[img_url]
    embed = disnake.Embed(title=anim_name, color=bot-color)
    embed.set_image(url=image_url)
    embed.set_footer(text="Powered by " + api_name)
    return embed
    print()
  except requests.exceptions.RequestException as e:
    return (error_msg + {e})

# commands - ping
@bot.slash_command(description="Get the bot's latency")
async def ping(inter):
  embed = disnake.Embed(
    title="🏓 Pong!", 
    description=f"{bot.latency * 1000}ms",
    color=bot-color
  )
  await inter.response.send_message(embed=embed)

# 8 ball
@bot.slash_command(description="It's a magic 8 ball")
async def eightball(inter, message):
  embed = disnake.Embed(
    title="🎱 Magic 8 Ball",
    color=bot-color
  )
  embed.add_field(name="Question:", value=message, inline=True)
  embed.add_field(name="Answer:", value=random.choice(eightball_responses), inline=True)
  await inter.response.send_message(embed=embed)

# random emoji
@bot.slash_command(description="Random emoji, could be used as the bot's reaction")
async def emoji(inter):
  embed = disnake.Embed(
    title=f"{random.choice(emoji)} <- Random Emoji",
    color=bot-color
  )
  await inter.response.send_message(embed=embed)

# reverse text
@bot.slash_command(description="Reverses your message")
async def reverse(inter, message):
  embed = disnake.Embed(title="◀️ Reverse", description=(message [::-1]))
  await inter.response.send_message(embed=embed)

# pop-it
@bot.slash_command(description="Pop-it made of text and spoilers")
async def popit(inter):
  embed = disnake.Embed(
    title="Pop It!",
    description="||⬜|| " * 50,
    color=bot-color
  )
  await inter.response.send_message(embed=embed)

# random animal image
@bot.slash_command(description="Get a random image of an animal")
async def animal(inter, type: str = commands.Param(choices=["cat", "dog", "duck", "fox", 'goose'])):
  await inter.response.defer()
  type = type.lower()

  # cat
  if type == "cat":
    await inter.followup.send(embed=randomAnimal('😺 Cat',  'https://cataas.com/cat?json=true', 'cataas.com', 'url', "Meow! Couldn't get a cat image: "))
  
  # dog
  elif type == "dog":
    await inter.followup.send(embed=randomAnimal('🐶 Dog',  'https://dog.ceo/api/breeds/image/random', 'dog.ceo', 'message', "Woof! Couldn't get a dog image: "))

  # duck
  elif type == "duck":
    await inter.followup.send(embed=randomAnimal('🦆 Duck',  'https://random-d.uk/api/quack', 'random-d.uk', 'url', "Quack! Couldn't get a duck image: "))

  # fox
  elif type == "fox":
    await inter.followup.send(embed=randomAnimal('🦊 Fox',  'https://randomfox.ca/floof', 'randomfox.ca', 'image', "(What does the fox say?) Couldn't get a fox image: "))
  
  # someone should realy make a random goose image service
  else:
    await inter.followup.send("Sorry, I don't have that animal yet")

# ai command made by the very ai this thing uses
@bot.slash_command(description="Chat with Gemini 2.0 Flash")
async def chatbot(inter, message: str):
  if not gemini_client:
      await inter.response.send_message("Sorry, the AI model is not configured correctly")
      return

  try:
    response = gemini_client.models.generate_content(
      model="gemini-2.0-flash-lite",
      contents=message,
      config={
        "system_instruction": bot_persona_instructions
      }
    )

    gemini_text_response = response.text

    if len(gemini_text_response) > 1024:
        gemini_text_response = gemini_text_response[:1021] + "..."

    embed = disnake.Embed(
        title="🤖 AI Chatbot ✨",
        color=bot-color
    )
    embed.add_field(name="Message:", value=message, inline=False)
    embed.add_field(name="Response:", value=gemini_text_response, inline=False)
    await inter.response.send_message(embed=embed)

  except Exception as e:
    print(f"Error during chatbot command: {e}")
    await inter.response.send_message(f"An error occurred while processing your request: {e}")
  if not gemini_client: # Use the initialized client
    await inter.response.send_message("Sorry, the AI model is not configured correctly. Please contact the bot developer.")
    return

  try:
    # Pass the system_instruction as part of the config dictionary
    # to the generate_content method for the new SDK.
    response = await gemini_client.models.generate_content(
      model="gemini-2.0-flash-lite", # Changed to 'lite' as discussed
      contents=message, # Just the user's message
      config={
        "system_instruction": bot_persona_instructions # Pass the persona here
      }
    )

    # Access the response text. The structure might be slightly different depending on the response type.
    # It's usually `response.text` for simple text generation.
    gemini_text_response = response.text

    # Truncate the response if it's too long (Discord embed field limit is 1024 chars)
    if len(gemini_text_response) > 1024:
      gemini_text_response = gemini_text_response[:1021] + "..." # Leave space for "..."

    embed = disnake.Embed(
      title="🤖 AI Chatbot ✨",
      color=bot-color
    )
    embed.add_field(name="Message:", value=message, inline=False)
    embed.add_field(name="Response:", value=gemini_text_response, inline=False)
    await inter.response.send_message(embed=embed)

  except Exception as e:
    print(f"Error during chatbot command: {e}")
    await inter.response.send_message(f"An error occurred while processing your request: {e}")

# random commmand responses and other vars
bot_color = 0x128056
eightball_responses = ["As I see it, yes.", "Ask again later.", "Better not tell you now.", "Cannot predict now.", "Concentrate and ask again.", "Don’t count on it.", "It is certain.", "It is decidedly so.", "Most likely.", "My reply is no.", "My sources say no.", "Outlook not so good.", "Outlook good.", "Reply hazy, try again.", "Signs point to yes.", "Very doubtful.", "Without a doubt.", "Yes.", "Yes - definitely.", "You may rely on it."]
emoji = [* "😃😁😅🤣😭😉😗😘😍🥳🙃😜😇😏😌😐🤔🤫🥱🐧😱🙄😤🥺🙁🤐😨😯😲😳🤯😬😓😞😣😩😵😴"]
cmds_list = [
  "/ping (Get the bot's latency)",
  "/eightball (It's a magic 8 ball)"
  "/emoji (Random emoji, could be used as the bot's reaction)"
  "/reverse (Reverses your message)"
  "/popit (Pop-it made of text and spoilers)"
  "/animal (Get a random image of an animal - cat, dog, duck, fox)"
  "/chatbot (Chat with Gemini 2.0 Flash)"
]

bot.run(os.getenv("TOKEN"))
