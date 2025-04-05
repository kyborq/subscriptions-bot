from multiprocessing import Process
from app.database import init_db
import app.bot

if __name__ == "__main__":
  init_db()
  
  p_bot = Process(target=app.bot.main)
  p_bot.start()
  p_bot.join()