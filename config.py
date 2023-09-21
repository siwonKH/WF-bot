import os
from dotenv import load_dotenv

load_dotenv()

TEST_GUILD_ID = int(os.getenv('TEST_GUILD_ID'))
MANAGER_ROLE = int(os.getenv('MANAGER_ROLE'))
MEMBER_ROLE = int(os.getenv('MEMBER_ROLE'))
TOTAL_CHANNEL = int(os.getenv('TOTAL_CHANNEL'))
MEMBER_CHANNEL = int(os.getenv('MEMBER_CHANNEL'))
BILL_CHANNEL = int(os.getenv('BILL_CHANNEL'))
MONTH_CHANNEL = int(os.getenv('MONTH_CHANNEL'))
RECORD_CHANNEL = int(os.getenv('RECORD_CHANNEL'))
