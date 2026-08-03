import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import math
import json
import os

# BotFather ကနေ ရလာတဲ့ Token အသစ်ကို ဒီမှာ ထည့်ပါ (ရှေ့က token ကို revoke လုပ်ပြီးသားဖြစ်ရမယ်)
API_TOKEN = os.environ.get('BOT_TOKEN')
# @userinfobot ကနေ ရလာတဲ့ ZY ရဲ့ Telegram User ID ဂဏန်း (Report များ ပို့ရန်)
ADMIN_ID =  int(os.environ.get('ADMIN_ID'))
bot = telebot.TeleBot(API_TOKEN)

DATA_FILE = 'profiles.json'


# ---------- Data ကို ဖိုင်ထဲမှာ ထိန်းသိမ်းခြင်း (bot ပြန် run လျှင်လည်း data မပျောက်စေရန်) ----------
def load_profiles():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return {int(k): v for k, v in data.items()}
    return {}


def save_profiles():
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(user_profiles, f, ensure_ascii=False, indent=2)


user_profiles = load_profiles()


# ---------- Haversine Formula: km အကွာအဝေး တွက်ခြင်း ----------
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    return R * c


# ---------- Profile Setup Flow ----------
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    user_profiles[chat_id] = {
        'gender': None, 'age': None,
        'latitude': None, 'longitude': None,
        'photo': None,
        'username': message.from_user.username,
        'liked': [], 'passed': [], 'matches': [],
        'blocked': [], 'report_count': 0
    }
    save_profiles()

    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(KeyboardButton('ကျား'), KeyboardButton('မ'))
    msg = bot.send_message(
        chat_id,
        "မင်္ဂလာပါ။ Profile ဆောက်ကြည့်ရအောင်။\nသင်က ကျား လား၊ မ လား ရွေးချယ်ပေးပါ -",
        reply_markup=markup
    )
    bot.register_next_step_handler(msg, process_gender_step)


def process_gender_step(message):
    chat_id = message.chat.id
    gender = message.text
    if gender not in ['ကျား', 'မ']:
        bot.send_message(chat_id, "ခလုတ်ကို နှိပ်ပြီး ရွေးချယ်ပေးပါ။")
        return
    user_profiles[chat_id]['gender'] = gender
    save_profiles()
    msg = bot.send_message(chat_id, "သင့်ရဲ့ အသက်ကို ဂဏန်းဖြင့် ရိုက်ထည့်ပေးပါ -")
    bot.register_next_step_handler(msg, process_age_step)


def process_age_step(message):
    chat_id = message.chat.id
    age = message.text
    if not age.isdigit() or int(age) < 18 or int(age) > 100:
        msg = bot.send_message(chat_id, "အသက် ၁၈ နှစ်အထက် ဂဏန်းစစ်စစ် ပြန်ရိုက်ပေးပါ -")
        bot.register_next_step_handler(msg, process_age_step)
        return
    user_profiles[chat_id]['age'] = age
    save_profiles()

    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(KeyboardButton('📍 Location ပို့မယ်', request_location=True))
    markup.add(KeyboardButton('ကျော်မယ်'))
    msg = bot.send_message(
        chat_id,
        "အနီးအနားရှိသူများနဲ့ Match ရအောင် Location ပို့ပေးပါ။\n(မလိုချင်ရင် 'ကျော်မယ်' နှိပ်ပါ)",
        reply_markup=markup
    )
    bot.register_next_step_handler(msg, process_location_step)


def process_location_step(message):
    chat_id = message.chat.id
    if message.content_type == 'location':
        user_profiles[chat_id]['latitude'] = message.location.latitude
        user_profiles[chat_id]['longitude'] = message.location.longitude
    save_profiles()
    msg = bot.send_message(chat_id, "နောက်ဆုံးအဆင့် - Profile ဓာတ်ပုံ ပို့ပေးပါ -")
    bot.register_next_step_handler(msg, process_photo_step)


def process_photo_step(message):
    chat_id = message.chat.id
    if message.content_type != 'photo':
        msg = bot.send_message(chat_id, "ဓာတ်ပုံပဲ ပြန်ပို့ပေးပါ -")
        bot.register_next_step_handler(msg, process_photo_step)
        return

    user_profiles[chat_id]['photo'] = message.photo[-1].file_id
    save_profiles()

    profile = user_profiles[chat_id]
    loc_text = "✅ ပါဝင်ပါတယ်" if profile.get('latitude') else "❌ မပါပါ"
    caption = f"✨ Profile ✨\n👫 လိင်: {profile['gender']}\n🎂 အသက်: {profile['age']}\n📍 Location: {loc_text}"
    bot.send_photo(chat_id, profile['photo'], caption=caption)
    bot.send_message(chat_id, "Profile ပြီးပါပြီ။ /find နဲ့ အနီးအနား သူငယ်ချင်းများ ရှာပါ။")


# ---------- Find / Matching (Like-Skip) ----------
@bot.message_handler(commands=['find'])
def find_nearby(message):
    show_next_profile(message.chat.id)


def show_next_profile(chat_id):
    if chat_id not in user_profiles or not user_profiles[chat_id].get('photo'):
        bot.send_message(chat_id, "ပထမဆုံး /start နဲ့ Profile ဆောက်ပေးပါ။")
        return

    me = user_profiles[chat_id]
    seen = set(me.get('liked', []) + me.get('passed', []) + me.get('blocked', []))

    candidates = []
    for oid, prof in user_profiles.items():
        if oid == chat_id or oid in seen or not prof.get('photo'):
            continue
        # ငါ့ကို block ထားသူများကိုလည်း မပြပါ
        if chat_id in prof.get('blocked', []):
            continue
        dist = None
        if me.get('latitude') and prof.get('latitude'):
            dist = calculate_distance(me['latitude'], me['longitude'], prof['latitude'], prof['longitude'])
        candidates.append((dist if dist is not None else float('inf'), oid, prof))

    if not candidates:
        bot.send_message(chat_id, "အခုလောလောဆယ် ကြည့်စရာ Profile မရှိတော့ပါ။ နောက်မှ ပြန်စမ်းပါ။")
        return

    candidates.sort(key=lambda x: x[0])
    dist, oid, prof = candidates[0]
    dist_text = f"📍 {dist:.1f} km" if dist != float('inf') else "📍 Location မသိပါ"
    caption = f"👫 လိင်: {prof['gender']}\n🎂 အသက်: {prof['age']}\n{dist_text}"

    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("❤️ Like", callback_data=f"like_{oid}"),
        InlineKeyboardButton("⏭️ Skip", callback_data=f"pass_{oid}")
    )
    markup.row(
        InlineKeyboardButton("🚫 Report / Block", callback_data=f"report_{oid}")
    )
    bot.send_photo(chat_id, prof['photo'], caption=caption, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith(('like_', 'pass_', 'report_')))
def handle_swipe(call):
    chat_id = call.message.chat.id
    action, target_id_str = call.data.split('_')
    target_id = int(target_id_str)

    me = user_profiles[chat_id]

    if action == 'report':
        # ကိုယ့် block list ထဲ ထည့်လိုက်တာနဲ့ နောက်ထပ် ဒီလူကို ဘယ်တော့မှ ပြန်မတွေ့တော့ပါ
        me.setdefault('blocked', []).append(target_id)
        target = user_profiles.get(target_id, {})
        target['report_count'] = target.get('report_count', 0) + 1
        save_profiles()
        bot.answer_callback_query(call.id, "Report/Block လုပ်ပြီးပါပြီ။")

        # Admin ဆီ notification ပို့
        reporter_username = me.get('username') or str(chat_id)
        target_username = target.get('username') or str(target_id)
        try:
            bot.send_message(
                ADMIN_ID,
                f"🚫 Report တင်ခြင်း\nReporter: @{reporter_username}\nReported user: @{target_username} (ID: {target_id})\nစုစုပေါင်း Report ရသည့်အကြိမ်: {target['report_count']}"
            )
        except Exception:
            pass  # ADMIN_ID မှားနေရင် bot မရပ်စေရန်

        show_next_profile(chat_id)
        return

    if action == 'like':
        me.setdefault('liked', []).append(target_id)
        target = user_profiles.get(target_id, {})

        # နှစ်ဦးစလုံး like ချင်းတူရင် Match ဖြစ်တယ်
        if chat_id in target.get('liked', []):
            me.setdefault('matches', []).append(target_id)
            target.setdefault('matches', []).append(chat_id)

            my_username = me.get('username')
            target_username = target.get('username')

            my_contact = f"@{target_username}" if target_username else "(username မထားသေးသူ - Telegram ID ဖြင့်သာ ဆက်သွယ်နိုင်ပါမည်)"
            target_contact = f"@{my_username}" if my_username else "(username မထားသေးသူ - Telegram ID ဖြင့်သာ ဆက်သွယ်နိုင်ပါမည်)"

            bot.send_message(chat_id, f"🎉 Match ရပါပြီ! -> {my_contact}")
            bot.send_message(target_id, f"🎉 Match ရပါပြီ! -> {target_contact}")
    else:
        me.setdefault('passed', []).append(target_id)

    save_profiles()
    bot.answer_callback_query(call.id)
    show_next_profile(chat_id)


# ---------- ကိုယ့် Profile ကြည့်ခြင်း ----------
@bot.message_handler(commands=['myprofile'])
def my_profile(message):
    chat_id = message.chat.id
    if chat_id not in user_profiles or not user_profiles[chat_id].get('photo'):
        bot.send_message(chat_id, "Profile မရှိသေးပါ။ /start နဲ့ ဆောက်ပါ။")
        return
    profile = user_profiles[chat_id]
    matches = len(profile.get('matches', []))
    caption = f"✨ Profile ✨\n👫 လိင်: {profile['gender']}\n🎂 အသက်: {profile['age']}\n❤️ Match ရသူ: {matches} ယောက်"
    bot.send_photo(chat_id, profile['photo'], caption=caption)


@bot.message_handler(commands=['help'])
def help_cmd(message):
    bot.send_message(
        message.chat.id,
        "/start - Profile အသစ်ဆောက်ရန်\n/find - အနီးအနား user ရှာရန်\n/myprofile - ကိုယ့် Profile ကြည့်ရန်"
    )


print("Bot is running...")
bot.infinity_polling()
