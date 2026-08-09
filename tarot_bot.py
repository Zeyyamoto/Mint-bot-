import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import random
import json
import os

# BotFather ကနေ ရလာတဲ့ Token ကို ဒီမှာ ထည့်ပါ
API_TOKEN = os.environ.get('BOT_TOKEN')
# @userinfobot ကနေ ရလာတဲ့ ZY ရဲ့ Telegram User ID ဂဏန်း
ADMIN_ID = int(os.environ.get('ADMIN_ID'))

# KPay မုန့်ကျွေးရန် အချက်အလက်
KPAY_NUMBER = "09798026034"
KPAY_NAME = "U Zay Ya (Account Name)"

bot = telebot.TeleBot(API_TOKEN)

DATA_FILE = 'tarot_users.json'
MONTHLY_FILE = 'monthly_horoscope.json'


# ---------- User Data (draw count စသည်) ----------
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


# ---------- Monthly Zodiac Horoscope + Yadaya (Admin ကနေ ပြင်နိုင်သည်) ----------
ZODIAC_LIST = [
    "မိဿ", "ပြိဿနော်", "မေထုန်", "ကရကဋ်", "သိဟ်", "ကန်",
    "တူ", "မြိုက်", "ဓနု", "မကာရ", "ကုမ္ဘ", "မိန်"
]


def load_monthly():
    if os.path.exists(MONTHLY_FILE):
        with open(MONTHLY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "month_label": "မထည့်ရသေးပါ",
        "zodiac": {z: "ဒီလအတွက် ဟောစာတမ်း Admin မှ မထည့်ရသေးပါ။" for z in ZODIAC_LIST},
        "yadaya": "ဒီလအတွက် ယတြာ Admin မှ မထည့်ရသေးပါ။"
    }


def save_monthly():
    with open(MONTHLY_FILE, 'w', encoding='utf-8') as f:
        json.dump(monthly_data, f, ensure_ascii=False, indent=2)


monthly_data = load_monthly()


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

# Reversed ကတ်အတွက် ယေဘုယျ modifier (ကတ်တိုင်း သီးခြား reversed meaning မလိုအောင် ရိုးရှင်းအောင် ပြုလုပ်ထားသည်)
REVERSED_NOTE = "🔄 ဒီကတ်က မှောက်ထွက်လာပါတယ် — အထက်ပါ အချက်ပြချက်ရဲ့ စွမ်းအင်က နှေးကွေး/ပိတ်ဆို့နေသေးတယ်လို့ ဆိုလိုပါတယ်။ သည်းခံပြီး အချိန်ပေးကြည့်ပါ။"

FOCUS_AREAS = [
    ("💼 အလုပ်", ["အောင်မြင်မှုအတွက် အားထုတ်မှုကို ဆက်ထားပါ။", "စိတ်ရှည်ရှည်နဲ့ ဆက်လုပ်ရင် ရလဒ်ကောင်း ရနိုင်ပါတယ်။", "လုပ်ဖော်ကိုင်ဖက်များနဲ့ ပွင့်ပွင့်လင်းလင်း ဆွေးနွေးပါ။"]),
    ("💞 ချစ်ရေး", ["နှလုံးသားရဲ့ အသံကို ယုံကြည်ပါ။", "ဆက်ဆံရေးထဲ ရိုးသားမှုက အရေးကြီးဆုံးပါ။", "စိတ်ရှည်ရှည်ထားပြီး နားလည်မှုတည်ဆောက်ပါ။"]),
    ("🩺 ကျန်းမာရေး", ["အနားယူချိန် လုံလောက်အောင် ယူပါ။", "စိတ်ဖိစီးမှုကို လျှော့ချဖို့ ကြိုးစားပါ။", "ခန္ဓာကိုယ်ရဲ့ အချက်ပြချက်ကို နားထောင်ပါ။"]),
]


# ---------- ၈ရက်နေ့ဗေဒင် (မွေးနေ့ဗေဒင် — Evergreen Content) ----------
BIRTHDAY_ZODIAC = {
    "တနင်္ဂနွေ": {
        "planet": "နေ", "color": "ပန်းရောင်", "direction": "အရှေ့မြောက်",
        "text": "ခေါင်းဆောင်မှုဉာဏ်ကောင်းပြီး ယုံကြည်မှုအပြည့်ရှိသူများ ဖြစ်ကြပါတယ်။ ဆုံးဖြတ်ချက်များကို ယုံကြည်စွာ ချမှတ်နိုင်ပေမယ့် တစ်ခါတစ်ရံ စိတ်တိုနိုင်ပါတယ်။ ယနေ့ခေတ်မှာ အလုပ်ခွင်ထဲ ခေါင်းဆောင်ရာထူးများနဲ့ အသင့်တော်ဆုံးပါ။"
    },
    "တနင်္လာ": {
        "planet": "လ", "color": "ဖြူရောင်", "direction": "အရှေ့",
        "text": "စိတ်ခံစားမှု နူးညံ့ပြီး ကရုဏာစိတ် ထားတတ်သူများ ဖြစ်ကြပါတယ်။ အနုပညာဆိုင်ရာ ဉာဏ်ကောင်းတတ်ပြီး မိသားစုကို တန်ဖိုးထားသူများ ဖြစ်ကြပါတယ်။ စိတ်ခံစားမှု အတက်အကျများနိုင်တာကို သတိထားပါ။"
    },
    "အင်္ဂါ": {
        "planet": "အင်္ဂါ", "color": "လိမ္မော်ရောင်", "direction": "တောင်",
        "text": "စွမ်းအင်ပြည့်ဝပြီး လုပ်ငန်းခွင်မှာ တက်ကြွသူများ ဖြစ်ကြပါတယ်။ ရဲရင့်ပြီး စိန်ခေါ်မှုများကို မကြောက်တတ်သူများ ဖြစ်ပေမယ့် စိတ်တိုနိုင်တာကို ထိန်းထားသင့်ပါတယ်။"
    },
    "ဗုဒ္ဓဟူး (နေ့)": {
        "planet": "ဗုဒ္ဓဟူး", "color": "အစိမ်းရောင်", "direction": "အနောက်တောင်",
        "text": "ဆက်သွယ်ရေးကျွမ်းကျင်ပြီး လူပြောကောင်းသူများ ဖြစ်ကြပါတယ်။ ဉာဏ်ရည်ထက်မြက်ပြီး သင်ယူမှုမြန်ဆန်သူများ ဖြစ်ကြပါတယ်။ အသစ်အဆန်းများကို လက်ခံနိုင်စွမ်း ရှိပါတယ်။"
    },
    "ဗုဒ္ဓဟူး (ည / ရာဟု)": {
        "planet": "ရာဟု", "color": "မီးခိုးရောင်", "direction": "အနောက်မြောက်",
        "text": "လျှို့ဝှက်ဆန်းကျယ်တာများကို စိတ်ဝင်စားပြီး နက်နဲစွာ စဉ်းစားတတ်သူများ ဖြစ်ကြပါတယ်။ အလွန်အမင်း လုပ်တတ်တဲ့ ဗီဇရှိတတ်လို့ ဟန်ချက်ညီအောင် ထိန်းသိမ်းပါ။"
    },
    "ကြာသပတေး": {
        "planet": "ကြာသပတေး", "color": "အဝါရောင်", "direction": "တောင်ပိုင်း",
        "text": "ပညာရေးကို တန်ဖိုးထားပြီး ရိုးသားဖြောင့်မတ်သူများ ဖြစ်ကြပါတယ်။ ကျွမ်းကျင်ဆရာများ၊ ကုသရေးလုပ်ငန်းများနဲ့ အသင့်တော်ဆုံးပါ။ အထူးသဖြင့် ကံကောင်းသော ကြယ်တာရာဖြစ်ပါတယ်။"
    },
    "သောကြာ": {
        "planet": "သောကြာ", "color": "ခရမ်းရောင်", "direction": "မြောက်",
        "text": "အလှအပ၊ ချစ်ခြင်းမေတ္တာနဲ့ ဆက်စပ်တဲ့ကိစ္စများကို ဉာဏ်ကောင်းသူများ ဖြစ်ကြပါတယ်။ ဖန်တီးမှုဉာဏ် ကောင်းမွန်ပြီး လူမှုဆက်ဆံရေး ကျွမ်းကျင်သူများ ဖြစ်ကြပါတယ်။"
    },
    "စနေ": {
        "planet": "စနေ", "color": "အနက်ရောင်", "direction": "အနောက်",
        "text": "စည်းကမ်းရှိပြီး အလုပ်ကြိုးစားတတ်သူများ ဖြစ်ကြပါတယ်။ ရေရှည်စီမံကိန်းများနဲ့ အသင့်တော်ဆုံးပါ။ သည်းခံမှုနဲ့ ဆက်လုပ်ရင် ရေရှည် အောင်မြင်မှုများ ရနိုင်ပါတယ်။"
    },
}


# ---------- Main Menu ----------
def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton('🔮 ကတ်ဖွင့်မယ်'))
    markup.row(KeyboardButton('🎂 မွေးနေ့ဗေဒင်'), KeyboardButton('✨ လစဉ်ဟောစာတမ်း'))
    markup.row(KeyboardButton('☕ ဘယ်သူမုန့်ကျွေးမှာလဲ'), KeyboardButton('ℹ️ Bot အကြောင်း'))
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
        "🔮 မင်္ဂလာပါ။\nတားရော့ ကတ်ဖွင့်ခြင်း၊ မွေးနေ့ဗေဒင်၊ လစဉ်ရာသီဖွား ဟောစာတမ်းများကို ဒီ Bot ကနေ ကြည့်နိုင်ပါတယ်။\n\n"
        "👇 Menu ကနေ ရွေးချယ်နိုင်ပါတယ်",
        reply_markup=main_menu()
    )


@bot.message_handler(commands=['help'])
def help_cmd(message):
    bot.send_message(
        message.chat.id,
        "/start - Bot စတင်ရန်\n/draw - ကတ်ဖွင့်ရန်\n\nMenu ခလုတ်များကိုလည်း သုံးနိုင်ပါတယ်။"
    )


# ---------- Tarot Card ----------
@bot.message_handler(commands=['draw'])
def draw_command(message):
    draw_card(message.chat.id)


@bot.message_handler(func=lambda m: m.text == '🔮 ကတ်ဖွင့်မယ်')
def menu_draw(message):
    draw_card(message.chat.id)


def draw_card(chat_id):
    if chat_id not in user_data:
        user_data[chat_id] = {'username': None, 'draw_count': 0}

    card_name, card_meaning = random.choice(CARDS)
    is_reversed = random.random() < 0.35  # ၃၅% ခန့် reversed ဖြစ်နိုင်ခြေ
    focus_label, focus_lines = random.choice(FOCUS_AREAS)
    focus_line = random.choice(focus_lines)

    user_data[chat_id]['draw_count'] = user_data[chat_id].get('draw_count', 0) + 1
    save_data()

    text = f"🔮 သင့်ရဲ့ ကတ်မှာ...\n\n{card_name}\n\n{card_meaning}"
    if is_reversed:
        text += f"\n\n{REVERSED_NOTE}"
    text += f"\n\n{focus_label} — {focus_line}"

    bot.send_message(chat_id, text)


# ---------- မွေးနေ့ဗေဒင် (၈ရက်) ----------
@bot.message_handler(func=lambda m: m.text == '🎂 မွေးနေ့ဗေဒင်')
def menu_birthday(message):
    show_birthday_menu(message.chat.id)


def show_birthday_menu(chat_id):
    markup = InlineKeyboardMarkup(row_width=2)
    for day in BIRTHDAY_ZODIAC.keys():
        markup.add(InlineKeyboardButton(day, callback_data=f"bday_{day}"))
    bot.send_message(chat_id, "🎂 သင်မွေးဖွားသည့် နေ့ကို ရွေးချယ်ပါ -", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('bday_'))
def callback_birthday(call):
    day = call.data.replace('bday_', '')
    info = BIRTHDAY_ZODIAC.get(day)
    bot.answer_callback_query(call.id)
    if not info:
        return
    text = (
        f"🎂 {day} သားများအတွက်\n\n"
        f"🪐 ကျမ်းဂြိုဟ် - {info['planet']}\n"
        f"🎨 ကံကောင်းရောင် - {info['color']}\n"
        f"🧭 ကံကောင်းအရပ် - {info['direction']}\n\n"
        f"{info['text']}"
    )
    bot.send_message(call.message.chat.id, text)


# ---------- လစဉ် ရာသီဖွားဟောစာတမ်း + ယတြာ ----------
@bot.message_handler(func=lambda m: m.text == '✨ လစဉ်ဟောစာတမ်း')
def menu_monthly(message):
    show_zodiac_menu(message.chat.id)


def show_zodiac_menu(chat_id):
    markup = InlineKeyboardMarkup(row_width=3)
    buttons = [InlineKeyboardButton(z, callback_data=f"zod_{z}") for z in ZODIAC_LIST]
    markup.add(*buttons)
    bot.send_message(
        chat_id,
        f"✨ {monthly_data.get('month_label', '')} အတွက် ရာသီဖွား ဟောစာတမ်း\n\nသင့်ရာသီကို ရွေးချယ်ပါ -",
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith('zod_'))
def callback_zodiac(call):
    zodiac = call.data.replace('zod_', '')
    text_body = monthly_data.get('zodiac', {}).get(zodiac, "ဒီလအတွက် ဟောစာတမ်း Admin မှ မထည့်ရသေးပါ။")
    bot.answer_callback_query(call.id)

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🪄 ဒီလ ယတြာ ကြည့်ရန်", callback_data="yadaya"))

    text = f"✨ {zodiac} ({monthly_data.get('month_label', '')})\n\n{text_body}"
    bot.send_message(call.message.chat.id, text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'yadaya')
def callback_yadaya(call):
    bot.answer_callback_query(call.id)
    text = f"🪄 {monthly_data.get('month_label', '')} အတွက် ယတြာ\n\n{monthly_data.get('yadaya', '')}"
    bot.send_message(call.message.chat.id, text)


# ---------- Admin: လစဉ်ဟောစာတမ်း/ယတြာ ပြင်ဆင်ခြင်း ----------
@bot.message_handler(commands=['setmonth'])
def set_month_label(message):
    if message.chat.id != ADMIN_ID:
        return
    try:
        label = message.text.split(' ', 1)[1]
    except IndexError:
        bot.send_message(message.chat.id, "အသုံးပြုပုံ: /setmonth ဩဂုတ်လ ၂၀၂၆")
        return
    monthly_data['month_label'] = label
    save_monthly()
    bot.send_message(message.chat.id, f"✅ လအမည် '{label}' ဖြင့် Update ပြီးပါပြီ။")


@bot.message_handler(commands=['setzodiac'])
def set_zodiac_text(message):
    if message.chat.id != ADMIN_ID:
        return
    # အသုံးပြုပုံ: /setzodiac မိဿ [ဟောစာတမ်းစာသား...]
    try:
        parts = message.text.split(' ', 2)
        zodiac = parts[1]
        text = parts[2]
    except IndexError:
        bot.send_message(
            message.chat.id,
            "အသုံးပြုပုံ:\n/setzodiac မိဿ ဒီလအတွက် ဟောစာတမ်းစာသား...\n\nရာသီစာရင်း: " + ", ".join(ZODIAC_LIST)
        )
        return

    if zodiac not in ZODIAC_LIST:
        bot.send_message(message.chat.id, "ရာသီအမည် မှားနေပါတယ်။ ဒီစာရင်းထဲက တစ်ခုသုံးပါ:\n" + ", ".join(ZODIAC_LIST))
        return

    monthly_data.setdefault('zodiac', {})[zodiac] = text
    save_monthly()
    bot.send_message(message.chat.id, f"✅ {zodiac} အတွက် ဟောစာတမ်း Update ပြီးပါပြီ။")


@bot.message_handler(commands=['setyadaya'])
def set_yadaya_text(message):
    if message.chat.id != ADMIN_ID:
        return
    try:
        text = message.text.split(' ', 1)[1]
    except IndexError:
        bot.send_message(message.chat.id, "အသုံးပြုပုံ: /setyadaya ဒီလအတွက် ယတြာစာသား...")
        return
    monthly_data['yadaya'] = text
    save_monthly()
    bot.send_message(message.chat.id, "✅ ယတြာ Update ပြီးပါပြီ။")


# ---------- KPay Tip / မုန့်ကျွေးခြင်း (Menu ထဲမှာသာ) ----------
@bot.message_handler(func=lambda m: m.text == '☕ ဘယ်သူမုန့်ကျွေးမှာလဲ')
def menu_tip(message):
    show_tip_info(message.chat.id)


def show_tip_info(chat_id):
    text = (
        "☕ ဘယ်သူမုန့်ကျွေးမှာလဲ\n\n"
        f"📲 KPay နံပါတ် - {KPAY_NUMBER}\n"
        f"👤 အမည် - {KPAY_NAME}\n\n"
        "ကျေးဇူးအများကြီးတင်ပါတယ် 🙏💛"
    )
    bot.send_message(chat_id, text)


# ---------- Bot အကြောင်း ----------
@bot.message_handler(func=lambda m: m.text == 'ℹ️ Bot အကြောင်း')
def about_cmd(message):
    bot.send_message(
        message.chat.id,
        "🔮 ဒီ Bot ကို ဖျော်ဖြေရေးအတွက်သာ ရည်ရွယ်ပါတယ်။ Tarot ကတ်ဖွင့်ခြင်း၊ မွေးနေ့ဗေဒင်၊ "
        "လစဉ်ရာသီဖွား ဟောစာတမ်းနဲ့ ယတြာများကို ကြည့်ရှုနိုင်ပါတယ်။\n\n"
        "အကုန်လုံး အခမဲ့ပါ — ကြိုက်ရင် Menu ထဲက ☕ ခလုတ်ကနေ မုန့်ကျွေးနိုင်ပါတယ်။"
    )


print("Tarot Bot is running...")
bot.infinity_polling()
