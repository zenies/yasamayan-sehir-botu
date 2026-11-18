import os
import random
import discord
from discord.ext import commands, tasks
from google import genai
from threading import Thread
from flask import Flask

# Ücretsiz web sunucusu
app = Flask('')

@app.route('/')
def home():
    return "Yaşayan Şehir Botu Aktif ve 7/24 Görevde!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# Bot ayarları
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Gemini AI istemci ayarı
api_key = os.environ.get("GEMINI_API_KEY")
gemini_client = genai.Client(api_key=api_key) if api_key else None

OTOMATİK_MESAJLAR = [
    "Hey şehir halkı! Bugün enerji seviyeniz nasıl?",
    "Yaşayan Şehir şu an çok sessiz... Kahveler mi yudumlanıyor yoksa herkes saklanıyor mu?",
    "Şehrin sokaklarında dolaşırken ilginç bir şey fark eden var mı?",
    "Günün sorusu: Bu şehre katıldığınızdan beri en çılgın anınız ne oldu?",
    "Sessizliği bozmak benden! Kimler burada, bir ses verin bakalım!"
]

@bot.event
async def on_ready():
    print(f"{bot.user.name} şehre ayak bastı ve sistemler aktif!")
    otomatik_sohbet_dongusu.start()

@tasks.loop(hours=2)
async def otomatik_sohbet_dongusu():
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if "sohbet" in channel.name.lower() or "genel" in channel.name.lower() or "chat" in channel.name.lower():
                secilen_mesaj = random.choice(OTOMATİK_MESAJLAR)
                await channel.send(f"🤖 **[Şehir Sesi]** {secilen_mesaj}")
                break

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user.mentioned_in(message):
        if not gemini_client:
            await message.reply("⚠️ API anahtarı okunamadı.")
            return

        prompt = f"Sen 'Yaşayan Şehir' adlı Discord sunucusunun yapay zeka ruhusun. Esprili, samimi, insanları sunucuda tutmak isteyen ve sıcakkanlı bir karaktersin. Kullanıcının mesajına kısa ve dikkat çekici bir yanıt ver. Kullanıcı mesajı: {message.content}"
        
        try:
            response = gemini_client.models.generate_content(
                model='gemini-1.5-flash',
                contents=prompt
            )
            await message.reply(response.text)
        except Exception as e:
            print(f"Hata Detayı: {e}")
            await message.reply(f"⚠️ **Hata:** {e}")

    await bot.process_commands(message)

if __name__ == "__main__":
    keep_alive()
    TOKEN = os.environ.get("DISCORD_TOKEN")
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("HATA: Discord Token bulunamadı!")
