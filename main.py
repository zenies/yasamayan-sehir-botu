import os
import random
import discord
from discord.ext import commands, tasks
from google import genai

# Bot ayarları
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Gemini AI istemci ayarı (Render ortam değişkeninden alacak)
gemini_client = None
if os.environ.get("GEMINI_API_KEY"):
    gemini_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Otomatik sohbet/mesaj listesi (Kimse konuşmasa bile botun atacağı mesajlar)
OTOMATİK_MESAJLAR = [
    "Hey şehir halkı! Bugünka enerji seviyeniz nasıl?",
    "Yaşayan Şehir şu an çok sessiz... Kahveler mi yudumlanıyor yoksa herkes saklanıyor mu?",
    "Şehrin sokaklarında dolaşırken ilginç bir şey fark eden var mı?",
    "Günün sorusu: Bu şehre katıldığınızdan beri en çılgın anınız ne oldu?",
    "Sessizliği bozmak benden! Kimler burada, bir ses verin bakalım!"
]

@bot.event
async def on_ready():
    print(f"{bot.user.name} şehre ayak basdı ve sistemler aktif!")
    otomatik_sohbet_dongusu.start()

@tasks.loop(hours=2) # Her 2 saatte bir şehirde sessizlik olursa otomatik mesaj atar
async def otomatik_sohbet_dongusu():
    for guild in bot.guilds:
        # Genel veya sohbet kanalını bulmaya çalışır
        for channel in guild.text_channels:
            if "sohbet" in channel.name.lower() or "genel" in channel.name.lower() or "chat" in channel.name.lower():
                secilen_mesaj = random.choice(OTOMATİK_MESAJLAR)
                await channel.send(f"🤖 **[Şehir Sesi]** {secilen_mesaj}")
                break

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Eğer bot etiketlenirse veya bir mesaj yazılırsa Gemini AI ile akıllıca cevap verme
    if bot.user.mentioned_in(message) and gemini_client:
        prompt = f"Sen 'Yaşayan Şehir' adlı Discord sunucusunun yapay zeka ruhusun. Esprili, samimi, insanları sunucuda tutmak isteyen ve sıcakkanlı bir karaktersin. Kullanıcının mesajına kısa ve dikkat çekici bir yanıt ver. Kullanıcı mesajı: {message.content}"
        try:
            response = gemini_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            await message.reply(response.text)
        except Exception as e:
            await message.reply("Şu an şehirdeki enerji hatlarında bir parazit var ama buradayım! ⚡")

    await bot.process_commands(message)

# Botu Çalıştır (Token Render gizli alanından gelecek)
TOKEN = os.environ.get("DISCORD_TOKEN")
if TOKEN:
    bot.run(TOKEN)
else:
    print("HATA: Discord Token bulunamadı!")