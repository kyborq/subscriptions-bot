from datetime import datetime
from dotenv import load_dotenv
from telegram import LabeledPrice, Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, PreCheckoutQueryHandler, filters
import os

from database import add_subscription, check_subscription, renew_subscription
from utils import e

load_dotenv()
telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await update.message.reply_text("Hello! Bot is working!")

async def purchase_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
  user_id = update.effective_user.id
  user_subscription = check_subscription(user_id)
  
  if user_subscription == None:
    await context.bot.send_message(
      chat_id=user_id, 
      text=e("*😿 Статус подписки*\n\nНа данный момент у вас нет подписки... Но вы можете её оплатить!"),
      parse_mode=ParseMode.MARKDOWN_V2
    )
    await context.bot.send_invoice(
      chat_id=update.effective_chat.id,
      title="Доступ к API",
      description="Купить доступ к API за звезды",
      payload="purchase_subscription",
      currency="XTR",
      prices=[LabeledPrice("1 Star", 1)],
      start_parameter="buy_stars",
      provider_token="",
      need_email=False,
    )
    return

  end_date = datetime.strptime(user_subscription[1], '%Y-%m-%d')
  today = datetime.today()
  days_until_end = (end_date - today).days

  if today > end_date:
    await context.bot.send_message(
      chat_id=user_id, 
      text=e("*⚠️ Статус подписки*\n\nПодписка истекла! Чтобы возобновить, используйте команду\n\n/renew"),
      parse_mode=ParseMode.MARKDOWN_V2
    )
  else:
    days_until_end = (end_date - today).days
    await context.bot.send_message(
      chat_id=user_id, 
      text=e(f"*⭐ Статус подписки*\n\nПодписка действует до {user_subscription[1]}\nОсталось дней: {days_until_end}"),
      parse_mode=ParseMode.MARKDOWN_V2
    )

async def renew_subscription_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
  user_id = update.effective_user.id
  user_subscription = check_subscription(user_id)

  end_date = datetime.strptime(user_subscription[1], '%Y-%m-%d')
  today = datetime.today()

  if today > end_date:
    await context.bot.send_invoice(
      chat_id=update.effective_chat.id,
      title="Доступ к API",
      description="Возобновить доступ к API за звезды",
      payload="renew_subscription",
      currency="XTR",
      prices=[LabeledPrice("1 Star", 1)],
      start_parameter="renew_stars",
      provider_token="",
      need_email=False,
    )
    return
  
  await context.bot.send_message(
    chat_id=user_id, 
    text=e("✅ С вашей подпиской все нормально, продлевать не нужно"),
    parse_mode=ParseMode.MARKDOWN_V2
  )

async def pre_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
  query = update.pre_checkout_query
  await query.answer(ok=True)

async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
  user_id = update.effective_user.id
  user_subscription = check_subscription(user_id)

  if user_subscription == None:
    add_subscription(user_id)
  else:
    renew_subscription(user_id)
  
  await update.message.reply_text("✅ Подписка оплачена! Спасибо 💘")

def main():
  builder = Application.builder()
  bot = builder.token(telegram_bot_token)
  app = bot.build()
    
  app.add_handler(CommandHandler("start", start_command))
  app.add_handler(CommandHandler("subscription", purchase_subscription))
  app.add_handler(CommandHandler("renew", renew_subscription_command))
  app.add_handler(PreCheckoutQueryHandler(pre_checkout))
  app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))
    
  app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
  main()
