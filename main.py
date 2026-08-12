import os
import aiohttp
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Token to'g'ridan-to'g'ri kodning o'ziga yozildi
TELEGRAM_BOT_TOKEN = "8929208171:AAFC41QUvc0pMWvf9Hr0yANdGCTI8vuYVcg"
ADMIN_PASSWORD = "7777"

admin_users = set()
user_balances = {}
user_collections = {}


async def fetch_random_waifu():
  url = "https://api.waifu.im/search"
  async with aiohttp.ClientSession() as session:
    async with session.get(url) as response:
      if response.status == 200:
        data = await response.json()
        if "images" in data and len(data["images"]) > 0:
          return data["images"][0]["url"]
  return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  user_id = update.message.from_user.id
  if user_id not in user_balances:
    user_balances[user_id] = 0

  keyboard = [
      [
          InlineKeyboardButton(
              "💰 Mening balansim", callback_data="my_balance"
          )
      ],
      [
          InlineKeyboardButton(
              "🌸 Waifu sotib olish (100 token)", callback_data="buy_waifu"
          )
      ],
      [
          InlineKeyboardButton(
              "📦 Mening kolleksiyam", callback_data="my_collection"
          )
      ],
      [InlineKeyboardButton("🎁 Token yig'ish", callback_data="earn_tokens")],
  ]
  reply_markup = InlineKeyboardMarkup(keyboard)

  await update.message.reply_text(
      "👋 Waifu botga xush kelibsiz!\nTokenlar yig'ib internetdan noyob"
      " anime qahramonlarini qo'lga kiriting.",
      reply_markup=reply_markup,
  )


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await update.message.reply_text(
      "🔐 Admin panelga kirish uchun maxfiy kodni yuboring.\nMasalan: `/code"
      " 7777`",
      parse_mode="Markdown",
  )


async def check_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
  user_id = update.message.from_user.id
  text = update.message.text

  if text.startswith("/code "):
    code = text.split(" ")[1]
    if code == ADMIN_PASSWORD:
      admin_users.add(user_id)
      keyboard = [
          [
              InlineKeyboardButton(
                  "💎 1 Million Token Qo'shish", callback_data="add_1m"
              )
          ],
          [
              InlineKeyboardButton(
                  "🚀 1 Milliard Token Qo'shish", callback_data="add_1b"
              )
          ],
          [
              InlineKeyboardButton(
                  "📊 Bot Statistikasi", callback_data="admin_stats"
              )
          ],
      ]
      reply_markup = InlineKeyboardMarkup(keyboard)
      await update.message.reply_text(
          "✅ Parol to'g'ri! Admin panel ochildi (Admin uchun barcha waifular"
          " bepul):",
          reply_markup=reply_markup,
      )
    else:
      await update.message.reply_text("❌ Xato parol!")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
  query = update.callback_query
  user_id = query.from_user.id
  await query.answer()

  if query.data == "my_balance":
    balance = user_balances.get(user_id, 0)
    await query.message.reply_text(f"💰 Sizning balansingiz: {balance} token")

  elif query.data == "earn_tokens":
    user_balances[user_id] = user_balances.get(user_id, 0) + 50
    await query.message.reply_text(
        "🎉 Tabriklaymiz! 50 ta token qo'shildi. Hozirgi balans:"
        f" {user_balances[user_id]}"
    )

  elif query.data == "buy_waifu":
    price = 100
    is_admin = user_id in admin_users
    current_balance = user_balances.get(user_id, 0)

    if is_admin or current_balance >= price:
      if not is_admin:
        user_balances[user_id] -= price

      waifu_url = await fetch_random_waifu()

      if waifu_url:
        if user_id not in user_collections:
          user_collections[user_id] = []
        user_collections[user_id].append(waifu_url)

        await query.message.reply_photo(
            photo=waifu_url,
            caption=(
                "✨ Tabriklaymiz! Siz yangi Waifu qo'lga kiritdingiz! 🎉"
                f"\nQolgan balansingiz: {user_balances.get(user_id, 'Cheksiz (Admin)')}"
            ),
        )
      else:
        await query.message.reply_text(
            "⚠️ Hozircha rasmni yuklab bo'lmadi, qaytadan urinib ko'ring."
        )
    else:
      await query.message.reply_text(
          "❌ Tokeningiz yetarli emas! (Narxi: 100 token). Token yig'ish"
          " bo'limidan token to'plang."
      )

  elif query.data == "my_collection":
    collection = user_collections.get(user_id, [])
    if not collection:
      await query.message.reply_text(
          "📦 Hozircha kolleksiyangiz bo'sh. Waifu sotib oling!"
      )
    else:
      await query.message.reply_text(
          f"📦 Siz jami {len(collection)} ta waifu yig'gansiz!"
      )
      for img_url in collection[-3:]:
        await query.message.reply_photo(photo=img_url)

  elif query.data == "back_home":
    keyboard = [
        [
            InlineKeyboardButton(
                "💰 Mening balansim", callback_data="my_balance"
            )
        ],
        [
            InlineKeyboardButton(
                "🌸 Waifu sotib olish (100 token)", callback_data="buy_waifu"
            )
        ],
        [
            InlineKeyboardButton(
                "📦 Mening kolleksiyam", callback_data="my_collection"
            )
        ],
        [InlineKeyboardButton("🎁 Token yig'ish", callback_data="earn_tokens")],
    ]
    await query.message.edit_text(
        "👋 Asosiy menyu:", reply_markup=InlineKeyboardMarkup(keyboard)
    )

  elif query.data in ["add_1m", "add_1b", "admin_stats"]:
    if user_id not in admin_users:
      await query.message.reply_text("⚠️ Sizda bu huquq yo'q!")
      return

    if query.data == "add_1m":
      user_balances[user_id] = user_balances.get(user_id, 0) + 1_000_000
      await query.message.reply_text(
          "✨ Admin uchun 1,000,000 token qo'shildi!"
      )
    elif query.data == "add_1b":
      user_balances[user_id] = user_balances.get(user_id, 0) + 1_000_000_000
      await query.message.reply_text(
          "🚀 Admin uchun 1,000,000,000 token qo'shildi!"
      )
    elif query.data == "admin_stats":
      await query.message.reply_text(
          f"📊 Statistika:\nJami foydalanuvchilar: {len(user_balances)}"
          f" ta\nAdminlar: {len(admin_users)} ta"
      )


def main():
  app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
  app.add_handler(CommandHandler("start", start))
  app.add_handler(CommandHandler("admin", admin_command))
  app.add_handler(
      MessageHandler(filters.TEXT & (~filters.COMMAND), check_code)
  )
  app.add_handler(CommandHandler("code", check_code))
  app.add_handler(CallbackQueryHandler(button_handler))

  print("Waifu API boti ishga tushdi...")
  app.run_polling()


if __name__ == "__main__":
  main()
    
