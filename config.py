import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    VK_TOKEN = os.getenv("VK_TOKEN")
    VK_GROUP_ID = int(os.getenv("VK_GROUP_ID", 0))
    DATABASE_PATH = os.getenv("DATABASE_PATH", "booking.db")

config = Config()