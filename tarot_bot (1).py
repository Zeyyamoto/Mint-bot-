import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import random
import json
import os

# BotFather ကနေ ရလာတဲ့ Token ကို ဒီမှာ ထည့်ပါ
API_TOKEN = os.environ.get('BOT_TOKEN')
# @userinfobot ကနေ ရလာတဲ့ ZY ရဲ့ Telegram User ID ဂဏန်း
ADMIN_ID = ADMIN_ID = int(os.environ.get('ADMIN_ID'))

# KPay မုန့်ကျွေးရန် အချက်အလက် (ZY ရဲ့ account နံပါတ်/နာမည်ကို ဒီမှာ ပြင်ပါ)
KPAY_NUMBER = "09798026034"
KPAY_NAME = "U Zay Ya (Account Name)"

bot = telebot.TeleBot(API_TOKEN)

DATA_FILE = 'tarot_users.json'


# ---------- Data ကို ဖိုင်ထဲ ထိန်းသိမ်းခြင်း ----------
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return {int(k): v for k, v in data.items()}
    return {}


def save_data():
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(user_data, f, ensure_ascii=False, indent=2)


user_data = load_data()


# ---------- Tarot Card Deck (Major Arcana 22 ကတ်) ----------
CARDS = [
    ("0. The Fool 🃏", "အသစ်တစ်ခု စတင်ဖို့ အချိန်ရောက်နေပါပြီ။ စိတ်ကူးအသစ်၊ ခရီးအသစ်တစ်ခုကို ကြောက်ရွံ့စရာမလိုဘဲ လက်ခံလိုက်ပါ။"),
    ("I. The Magician ✨", "သင့်လက်ထဲမှာ လိုအပ်တဲ့ အရာအားလုံး ရှိနှင့်ပြီးသားပါ။ ယုံကြည်မှုနဲ့ လုပ်ဆောင်ကြည့်ပါ။"),
    ("II. The High Priestess 🌙", "အတွင်းစိတ်ရဲ့ အသံကို နားထောင်ပါ။ အချိန်မရောက်သေးတဲ့ကိစ္စများကို စောင့်ဆိုင်းပါ။"),
    ("III. The Empress 🌸", "ကြွယ်ဝမှု၊ ချစ်ခြင်းမေတ္တာနဲ့ ဖန်တီးမှု ရှိသောကာလ။ ကိုယ့်ကိုယ်ကို ချစ်ခင်ဂရုစိုက်ပါ။"),
    ("IV. The Emperor 👑", "စည်းကမ်းရှိစွာ ဆုံးဖြတ်ချက်များ ချမှတ်ရမယ့်အချိန်။ ခိုင်မာမှုနဲ့ ရှေ့ဆက်ပါ။"),
    ("V. The Hierophant 📿", "အတွေ့အကြုံရှိသူများရဲ့ အကြံဉာဏ်ကို နားထောင်ကြည့်ပါ။ ရိုးရာအတိုင်း လုပ်ခြင်းက အကျိုးရှိနိုင်ပါတယ်။"),
    ("VI. The Lovers 💞", "ရွေးချယ်မှုတစ်ခု လာနေပါပြီ။ နှလုံးသားရဲ့ အသံကို လိုက်နာကြည့်ပါ။"),
    ("VII. The Chariot 🏇", "ရည်မှန်းချက်ဆီ တောက်လျှောက် ရှေ့ဆက်ရမယ့်အချိန်။ စိတ်ဓာတ်ခိုင်မာစွာ ဆက်သွားပါ။"),
    ("VIII. Strength 🦁", "ခက်ခဲမှုများကို နူးညံ့မှု၊ သည်းခံမှုနဲ့ ကျော်လွှားနိုင်ပါတယ်။ ကိုယ့်ကိုယ်ကို ယုံကြည်ပါ။"),
    ("IX. The Hermit 🕯️", "တစ်ယောက်တည်း အချိန်ယူပြီး စဉ်းစားသင့်တဲ့အချိန်။ အဖြေတွေက အတွင်းစိတ်ထဲမှာ ရှိပါတယ်။"),
    ("X. Wheel of Fortune 🎡", "ဘဝရဲ့ လှည့်ကွက်တစ်ခု ပြောင်းလဲတော့မယ်။ အခွင့်အလမ်းကောင်းများ ရောက်လာနိုင်ပါတယ်။"),
    ("XI. Justice ⚖️", "မျှတမှု၊ အမှန်တရားနဲ့ ဆုံးဖြတ်ချက်များ ချမှတ်ရမည့်အချိန်။ တာဝန်ယူမှုကို လေးစားပါ။"),
    ("XII. The Hanged Man 🙃", "ရှုထောင့်သစ်တစ်ခုနဲ့ ကြည့်ကြည့်ပါ။ စောင့်ဆိုင်းခြင်းကလည်း လုပ်ဆောင်မှုတစ်မျိုးပါ။"),
    ("XIII. Death 💀", "အဆုံးသတ်တစ်ခုက အစသစ်တစ်ခုကို ဖွင့်ပေးမှာပါ။ ပြောင်းလဲမှုကို မကြောက်ပါနဲ့။"),
    ("XIV. Temperance 🕊️", "ဟန်ချက်ညီညီ လုပ်ဆောင်ခြင်းက အောင်မြင်မှုရဲ့ သော့ချက်ပါ။ စိတ်ရှည်ပါ။"),
    ("XV. The Devil ⛓️", "ကိုယ့်ကိုယ်ကို ချုပ်နှောင်ထားတဲ့ အကျင့်/အတွေးများကို သတိထားမိပါစေ။ လွတ်မြောက်နိုင်ပါတယ်။"),
    ("XVI. The Tower 🗼", "မမျှော်လင့်ထားတဲ့ ပြောင်းလဲမှုတစ်ခု လာနိုင်ပါတယ်။ ဒါက ပိုကောင်းတဲ့အနာဂတ်အတွက် လမ်းဖွင့်ပေးမှာပါ။"),
    ("XVII. The Star ⭐", "မျှော်လင့်ချက်၊ ယုံကြည်မှုနဲ့ ကုသနိုင်မှု။ အနာဂတ်အတွက် ကောင်းသော အချက်ပြပါတယ်။"),
    ("XVIII. The Moon 🌕", "ရှင်းလင်းမှုမရှိသေးတဲ့ ကာလ။ စိတ်ခံစားချက်များကို လေ့လာကြည့်ပြီး သတိရှိစွာ လုပ်ဆောင်ပါ။"),
    ("XIX. The Sun ☀️", "ပျော်ရွှင်မှု၊ အောင်မြင်မှုနဲ့ ရှင်းလင်းတောက်ပမှု ရောက်လာမည့် အချက်ပြပါတယ်။"),
    ("XX. Judgement 📯", "အတိတ်ကို ပြန်သုံးသပ်ပြီး အသစ်တစ်ခုကို လက်ခံရန် အချိန်ကျရောက်ပါပြီ။"),
    ("XXI. The World 🌍", "စက်ဝန်းတစ်ခု ပြီးဆုံးသွားပါပြီ။ ပန်းတိုင်ရောက်ခြင်း၊ ပြီးပြည့်စုံခြင်းကို ခံစားရပါလိမ့်မယ်။"),
]


# ---------- Main Menu ----------
def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton('🔮 ကတ်ဖွင့်မယ်'))
    markup.row(KeyboardButton('☕ ဘယ်သူမုန့်ကျွေးမှာလဲ'), KeyboardButton('ℹ️ Bot အကြောင်း'))
    return markup


def tip_inline_button():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("☕ ဘယ်သူမုန့်ကျွေးမှာလဲ (KPay)", callback_data="tip"))
    return markup


# ---------- Commands ----------
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    if chat_id not in user_data:
        user_data[chat_id] = {'username': message.from_user.username, 'draw_count': 0}
        save_data()

    bot.send_message(
        chat_id,
        "🔮 မင်္ဂလာပါ။\nတားရော့ ကတ်ဖွင့်ပြီး ဒီနေ့အတွက် အချက်ပြချက်ကို ကြည့်ကြရအောင်။\n\n"
        "👇 'ကတ်ဖွင့်မယ်' ကို နှိပ်ပါ",
        reply_markup=main_menu()
    )


@bot.message_handler(commands=['draw'])
def draw_command(message):
    draw_card(message.chat.id)


@bot.message_handler(func=lambda m: m.text == '🔮 ကတ်ဖွင့်မယ်')
def menu_draw(message):
    draw_card(message.chat.id)


@bot.message_handler(func=lambda m: m.text == 'ℹ️ Bot အကြောင်း')
def about_cmd(message):
    bot.send_message(
        message.chat.id,
        "🔮 ဒီ Bot ကို ဖျော်ဖြေရေးအတွက်သာ ရည်ရွယ်ပါတယ်။ တားရော့ ကတ်တွေကို random ဖွင့်ပြီး နေ့စဉ်အတွက် အချက်ပြချက် ပေးပါတယ်။\n\n"
        "အကုန်လုံး အခမဲ့ပါ — ကြိုက်ရင် Admin ကို မုန့်ကျွေးနိုင်ပါတယ် ☕"
    )


def draw_card(chat_id):
    if chat_id not in user_data:
        user_data[chat_id] = {'username': None, 'draw_count': 0}

    card_name, card_meaning = random.choice(CARDS)
    user_data[chat_id]['draw_count'] = user_data[chat_id].get('draw_count', 0) + 1
    save_data()

    text = f"🔮 သင့်ရဲ့ ကတ်မှာ...\n\n{card_name}\n\n{card_meaning}"
    bot.send_message(chat_id, text, reply_markup=tip_inline_button())


# ---------- KPay Tip / မုန့်ကျွေးခြင်း ----------
@bot.message_handler(func=lambda m: m.text == '☕ ဘယ်သူမုန့်ကျွေးမှာလဲ')
def menu_tip(message):
    show_tip_info(message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data == 'tip')
def callback_tip(call):
    bot.answer_callback_query(call.id)
    show_tip_info(call.message.chat.id)


def show_tip_info(chat_id):
    text = (
        "☕ ဆရာမကို မုန့်ကျွေးရန်\n\n"
        f"📲 KPay နံပါတ် - {KPAY_NUMBER}\n"
        f"👤 အမည် - {KPAY_NAME}\n\n"
        "ကျေးဇူးအများကြီးတင်ပါတယ် 🙏💛"
    )
    bot.send_message(chat_id, text)


@bot.message_handler(commands=['help'])
def help_cmd(message):
    bot.send_message(
        message.chat.id,
        "/start - Bot စတင်ရန်\n/draw - ကတ်ဖွင့်ရန်\n\nMenu ခလုတ်များကိုလည်း သုံးနိုင်ပါတယ်။"
    )


print("Tarot Bot is running...")
bot.infinity_polling()
