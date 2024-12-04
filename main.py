import re
from typing import Final

import os
import aiohttp
from dotenv import load_dotenv
from discord import Intents, Client, Message

from responses import get_response

# Load the Discord token from the .env file
load_dotenv()
TOKEN: Final[str] = os.getenv("DISCORD_TOKEN")

# Load the Riot API URL from the .env file
load_dotenv()
RIOT_API_URL: Final[str] = os.getenv("RIOT_API_URL")

# Load the API key from the .env file
load_dotenv()
RIOT_API_KEY: Final[str] = os.getenv("RIOT_API_KEY")

# STEP 1: BOT SETUP: INTENTS AND CLIENT

intents: Intents = Intents.default()
intents.message_content = True
client: Client = Client(intents=intents)

# STEP 2: MESSAGE FUNCTIONALITY
async def get_account_info(game_name: str, tag_line: str) -> dict:
    url = f"{RIOT_API_URL}riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}?api_key={RIOT_API_KEY}"
    print(f"Fetching account info from URL: {url}")
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            print(f"Account info response status: {response.status}")
            if response.status == 200:
                return await response.json()
            else:
                return None

async def get_match_ids(puuid: str) -> list:
    url = f"{RIOT_API_URL}lol/match/v5/matches/by-puuid/{puuid}/ids?api_key={RIOT_API_KEY}"
    print(f"Fetching match IDs from URL: {url}")
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            print(f"Match IDs response status: {response.status}")
            if response.status == 200:
                return await response.json()
            else:
                return []

async def get_match_details(match_id: str) -> dict:
    url = f"{RIOT_API_URL}lol/match/v5/matches/{match_id}?api_key={RIOT_API_KEY}"
    print(f"Fetching match details from URL: {url}")
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            print(f"Match details response status: {response.status}")
            if response.status == 200:
                return await response.json()
            else:
                return None

async def did_player_win(match_id: str, puuid: str) -> bool:
    match_data = await get_match_details(match_id)
    if match_data:
        for participant in match_data['info']['participants']:
            if participant['puuid'] == puuid:
                return participant['win']
    return False

# STEP 2: MESSAGE FUNCTIONALITY

async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        print('(Message was empty because intents were not enabled probably)')
        return

    if is_private := user_message[0] == '?':
        user_message = user_message[1:]

    game_name_pattern = r"gameName:\s*(\w+),\s*tagLine:\s*(\w+)"
    match = re.match(game_name_pattern, user_message)

    if match:
        game_name, tag_line = match.groups()
        print(f"Extracted game name: {game_name}, tag line: {tag_line}")
        account_info = await get_account_info(game_name, tag_line)
        if account_info:
            puuid = account_info['puuid']
            print(f"Retrieved PUUID: {puuid}")
            match_ids = await get_match_ids(puuid)
            if match_ids:
                last_match_id = match_ids[0]
                print(f"Retrieved last match ID: {last_match_id}")
                player_won = await did_player_win(last_match_id, puuid)
                response_message = f"The player {game_name}#{tag_line} {'won' if player_won else 'lost'} their last game."
            else:
                response_message = "Failed to retrieve match IDs."
        else:
            response_message = "Failed to retrieve account information."
        
        await message.author.send(response_message) if is_private else await message.channel.send(response_message)
    else:
        try:
            response: str = get_response(user_message)
            await message.author.send(response) if is_private else await message.channel.send(response)
        except Exception as e:
            print(e)
        
        
# STEP 3: HANDLING THE STARTUP FOR OUR BOT
@client.event
async def on_ready() -> None:
    print(f'{client.user} has connected to Discord and is now running!')
    
    # STEP 4: HANDLING INCOMING MESSAGES
@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return
    
    username: str = str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)
    
    print(f'[{channel}] {username}: "{user_message}"')
    await send_message(message, user_message)
    
    # STEP 5: MAIN ENTRY POINT, RUN THE BOT
    
def main() -> None:
    client.run(TOKEN)

if __name__ == '__main__':
    main()