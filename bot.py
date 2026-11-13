import os, asyncio, time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
TOKEN = os.getenv("BOT_TOKEN")
games = {}
game_counter = {}
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot Tebak Dadu aktif!\n/tbk buka game\n/hl 37 isi hasil\n/stoptutup tebakan")
async def tbk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    if chat.type == "private":
        await update.message.reply_text("Masukin gue ke grup dulu!")
        return
    game_counter[chat.id] = game_counter.get(chat.id, 0) + 1
    no = game_counter[chat.id]
    games[chat.id] = {"no": no, "open": True, "bets": {}, "created": time.time()}
    await update.message.reply_text(f"GAME {no} DIBUKA\nKirim 1 angka 9-54, contoh 29\nTimer 25 detik")
    await asyncio.sleep(25)
    g = games.get(chat.id)
    if g and g["no"] == no and g["open"]:
        g["open"] = False
        await context.bot.send_message(chat.id, f"TEBAKAN DITUTUP - GAME {no}\n{len(g['bets'])} tebakan masuk")
async def stoptutup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    g = games.get(update.effective_chat.id)
    if not g or not g["open"]:
        await update.message.reply_text("Ga ada game yang kebuka.")
        return
    g["open"] = False
    await update.message.reply_text(f"TEBAKAN DITUTUP - GAME {g['no']}\n{len(g['bets'])} tebakan masuk")
async def terima_tebakan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    g = games.get(update.effective_chat.id)
    if not g or not g["open"]:
        return
    txt = update.message.text.strip()
    if not txt.isdigit():
        return
    angka = int(txt)
    if angka < 9 or angka > 54:
        return
    user = update.effective_user
    if user.id in g["bets"]:
        return
    g["bets"][user.id] = {"angka": angka, "nama": user.first_name, "time": time.time()}
async def hl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    g = games.get(update.effective_chat.id)
    if not g:
        await update.message.reply_text("Ga ada game.")
        return
    if not context.args:
        await update.message.reply_text("Pakai: /hl 37")
        return
    hasil = int(context.args[0].split("-")[0])
    g["open"] = False
    bets = sorted(list(g["bets"].values()), key=lambda x: x["time"])
    pemenang = [b for b in bets if b["angka"] == hasil]
    kategori = "B" if hasil >= 32 else "K"
    nama = pemenang[0]["nama"] if pemenang else "-"
    await update.message.reply_text(f"HASIL GAME {g['no']}\nAngka: {hasil} ({kategori})\nPEMENANG: {nama}\n{len(bets)} tebakan, {len(pemenang)} tepat")
    del games[update.effective_chat.id]
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    games.pop(update.effective_chat.id, None)
    await update.message.reply_text("Game dibatalin.")
async def resetgame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    game_counter[update.effective_chat.id] = 0
    games.pop(update.effective_chat.id, None)
    await update.message.reply_text("Nomor game balik ke 1.")
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("tbk", tbk))
    app.add_handler(CommandHandler("stoptutup", stoptutup))
    app.add_handler(CommandHandler("hl", hl))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("resetgame", resetgame))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, terima_tebakan))
    print("Bot jalan...")
    app.run_polling()
