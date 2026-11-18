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

YOGUNLUK_CEVAPLARI = [
    "Kahve molasındayım, birazdan buradayım dostum! ☕",
    "Şehrin altyapısında ufak bir internet kopması oldu, dalgınlığıma ver. ⚡",
    "Şu an kafam biraz dolu, sokaklarda tur atıp geliyorum! 🏙️",
    "Aşırı bir kalabalık var, herkes bana yükleniyor! Soluklanıp döneceğim. 😄"
]

@bot.event
async def on_ready():
    print(f"{bot.user.name} şehre ayak bastı ve sistemler aktif!")
    
    # Bot açıldığında sunucuda eksik kanalları otomatik kurma görevi
    for guild in bot.guilds:
        existing_channels = [c.name for c in guild.channels]
        
        # Kategori yoksa oluştur
        category = discord.utils.get(guild.categories, name="🏛️ YAŞAYAN ŞEHİR")
        if not category:
            category = await guild.create_category("🏛️ YAŞAYAN ŞEHİR")
            
        # Kanalları kontrol et ve yoksa yarat
        required_channels = ["genel-sohbet", "oyun-odası", "itiraf-ve-sohbet"]
        for ch_name in required_channels:
            if ch_name not in existing_channels:
                await guild.create_text_channel(ch_name, category=category)
                print(f"Oluşturulan kanal: {ch_name}")

    otomatik_sohbet_dongusu.start()

@tasks.loop(hours=2)
async def otomatik_sohbet_dongusu():
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if "sohbet" in channel.name.lower() or "genel" in channel.name.lower():
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
            dogal_cevap = random.choice(YOGUNLUK_CEVAPLARI)
            await message.reply(dogal_cevap)

    await bot.process_commands(message)

if __name__ == "__main__":
    keep_alive()
    TOKEN = os.environ.get("DISCORD_TOKEN")
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("HATA: Discord Token bulunamadı!")
