import os
from dataclasses import dataclass

@dataclass
class Config:
    BOT_TOKEN: str = os.getenv('BOT_TOKEN', '7786703529:AAGr0NUfu2tYcQdYYpauCYWKzZs1Bzil-hE')
    DATA_FILE: str = 'togel_data.json'
    MAX_HISTORICAL_DATA: int = 1000
    PREDICTION_LINES: int = 4
    BBFS_DIGITS: int = 7