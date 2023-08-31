import os
import discord
from dotenv import load_dotenv

load_dotenv()

TEST_GUILD = discord.Object(int(os.getenv('TEST_GUILD')))
TEST_GUILD_ID = int(os.getenv('TEST_GUILD_ID'))
MANAGER_ROLE = int(os.getenv('MANAGER_ROLE'))
MEMBER_ROLE = int(os.getenv('MEMBER_ROLE'))
TOTAL_CHANNEL = int(os.getenv('TOTAL_CHANNEL'))
MEMBER_CHANNEL = int(os.getenv('MEMBER_CHANNEL'))
BILL_CHANNEL = int(os.getenv('BILL_CHANNEL'))
