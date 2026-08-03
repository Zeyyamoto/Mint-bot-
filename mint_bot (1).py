import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import math
import json
import os
import datetime

# ---------------- CONFIG (ဒီနေရာတွေကို ပြင်ပေးပါ) ----------------
API_TOKEN = 'ဒီနေရာမှာ_TOKEN_အသစ်_ထည့်ပါ'
ADMIN_ID = 123456789  # @userinfobot ကနေ ရလာတဲ့ Admin ID

KPAY_PHONE = '09xxxxxxxxx'      # KPay/KBZPay လက်ခံမယ့် ဖုန်းနံပါတ်
KPAY_NAME = 'အမည် ဒီနေရာမှာထည့်ပါ'  # Account holder name
VIP_PRICE_TEXT = '5,000 Ks / လ'    # ဈေးနှုန်း ပြင်ချင်ရင် ပြင်ပါ

FREE_DAILY_LIKES = 15   # VIP မဟုတ်သေးသူများအတွက် တစ်နေ့ Like ကန့်သတ်ချက်
AUTO_BAN_REPORTS = 5    # ဒီအကြိမ်ရေထက် Report ရလျှင် auto-hide လုပ်မည်
# --------------------------------------------------------------

bot = telebot.TeleBot(API_TOKEN)
DATA_FILE = 'profiles.json'


# ---------- Data ကို ဖိုင်ထဲမှာ ထိန်းသိမ်းခြင်း ----------
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


def today_str():
    return datetime.date.today().isoformat()


def ensure_daily_reset(profile):
    if profile.get('like_date') != today_str():
        profile['like_date'] = today_str()
        profile['likes_today'] = 0


def is_vip(profile):
    return bool(profile.get('vip', False))


# ---------- Haversine Formula: km အကွာအဝေး တွက်ခြင်း ----------
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    return R * c


# ---------- Bot Command Menu (Telegram ရဲ့ built-in menu icon) ----------
def setup_bot_commands():
    bot.set_my_commands([
        telebot.types.BotCommand('start', 'Profile အသစ်ဆောက်ရန်'),
        telebot.types.BotCommand('find', 'အနီးအနား user ရှာရန်'),
        telebot.types.BotCommand('myprofile', 'ကိုယ့် Profile ကြည့်ရန်'),
        telebot.types.BotCommand('editprofile', 'Profile ပြင်ရန် / ပြန်စရန်'),
        telebot.types.BotCommand('vip', 'VIP Member ဖြစ်ရန်'),
        telebot.types.BotCommand('likedme', 'ဘယ်သူတွေ Like လုပ်လဲ ကြည့်ရန် (VIP)'),
        telebot.types.BotCommand('safety', 'လုံခြုံရေး အကြံပြုချက်များ'),
        telebot.types.BotCommand('help', 'အကူအညီ'),
    ])


SAFETY_MESSAGE = (
    "⚠️ လုံခြုံရေး သတိပေးချက်\n\n"
    "• အသက် ၁၈ နှစ်အောက် မဟုတ်ကြောင်း သေချာပါစေ။\n"
    "• မသိကျွမ်းသေးသူကို ငွေ/ကိုယ်ရေးအချက်အလက် (နိုင်ငံသားစိစစ်ရေးကတ်၊ လိပ်စာ) ဘယ်တော့မှ မပေးပါနှင့်။\n"
    "• သံသယဖြစ်ဖွယ် သို့မဟုတ် ငွေတောင်းသူများကို 🚫 Report/Block နှိပ်ပါ။\n"
    "• ပထမဆုံးတွေ့ဆုံမှုများကို လူစည်ကားရာနေရာတွင် ရွေးချယ်ပါ။"
)


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
        'blocked': [], 'report_count': 0,
        'banned': False,
        'vip': False,
        'likes_today': 0, 'like_date': today_str(),
        'received_likes': [],
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
    bot.send_message(chat_id, SAFETY_MESSAGE)


# ---------- Profile ပြင်ရန် / ပြန်စရန် Menu ----------
@bot.message_handler(commands=['editprofile'])
def edit_profile_menu(message):
    chat_id = message.chat.id
    if chat_id not in user_profiles:
        bot.send_message(chat_id, "ပထမဆုံး /start နဲ့ Profile ဆောက်ပေးပါ။")
        return
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("🎂 အသက် ပြောင်းရန်", callback_data="edit_age"))
    markup.row(InlineKeyboardButton("📍 Location ပြောင်းရန်", callback_data="edit_location"))
    markup.row(InlineKeyboardButton("🖼️ ဓာတ်ပုံ ပြောင်းရန်", callback_data="edit_photo"))
    markup.row(InlineKeyboardButton("♻️ Profile အားလုံး ပြန်စရန်", callback_data="edit_reset"))
    bot.send_message(chat_id, "ဘာကို ပြင်ချင်ပါသလဲ?", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_'))
def handle_edit_menu(call):
    chat_id = call.message.chat.id
    action = call.data

    if action == 'edit_age':
        bot.answer_callback_query(call.id)
        msg = bot.send_message(chat_id, "အသက်အသစ်ကို ဂဏန်းဖြင့် ရိုက်ထည့်ပေးပါ -")
        bot.register_next_step_handler(msg, process_edit_age)

    elif action == 'edit_location':
        bot.answer_callback_query(call.id)
        markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add(KeyboardButton('📍 Location ပို့မယ်', request_location=True))
        msg = bot.send_message(chat_id, "Location အသစ်ပို့ပေးပါ -", reply_markup=markup)
        bot.register_next_step_handler(msg, process_edit_location)

    elif action == 'edit_photo':
        bot.answer_callback_query(call.id)
        msg = bot.send_message(chat_id, "ဓာတ်ပုံအသစ် ပို့ပေးပါ -")
        bot.register_next_step_handler(msg, process_edit_photo)

    elif action == 'edit_reset':
        bot.answer_callback_query(call.id)
        confirm = InlineKeyboardMarkup()
        confirm.row(
            InlineKeyboardButton("✅ ဟုတ်ကဲ့၊ ပြန်စမည်", callback_data="reset_confirm"),
            InlineKeyboardButton("❌ မလုပ်တော့ပါ", callback_data="reset_cancel"),
        )
        bot.send_message(
            chat_id,
            "⚠️ Profile အားလုံး (ဓာတ်ပုံ၊ Match များအပါအဝင်) ပျက်သွားပါမည်။ သေချာပါသလား?",
            reply_markup=confirm
        )


@bot.callback_query_handler(func=lambda call: call.data in ('reset_confirm', 'reset_cancel'))
def handle_reset_confirm(call):
    chat_id = call.message.chat.id
    if call.data == 'reset_confirm':
        bot.answer_callback_query(call.id, "Profile ပြန်စပြီးပါပြီ။")
        bot.send_message(chat_id, "Profile ကို အစကနေ ပြန်ဆောက်ကြရအောင် — /start ကို နှိပ်ပါ။")
    else:
        bot.answer_callback_query(call.id, "ပယ်ဖျက်လိုက်ပါပြီ။")
        bot.send_message(chat_id, "ဘာမှ ပြောင်းလဲမှု မရှိပါ။")


def process_edit_age(message):
    chat_id = message.chat.id
    age = message.text
    if not age.isdigit() or int(age) < 18 or int(age) > 100:
        msg = bot.send_message(chat_id, "အသက် ၁၈ နှစ်အထက် ဂဏန်းစစ်စစ် ပြန်ရိုက်ပေးပါ -")
        bot.register_next_step_handler(msg, process_edit_age)
        return
    user_profiles[chat_id]['age'] = age
    save_profiles()
    bot.send_message(chat_id, "✅ အသက် ပြောင်းပြီးပါပြီ။")


def process_edit_location(message):
    chat_id = message.chat.id
    if message.content_type == 'location':
        user_profiles[chat_id]['latitude'] = message.location.latitude
        user_profiles[chat_id]['longitude'] = message.location.longitude
        save_profiles()
        bot.send_message(chat_id, "✅ Location ပြောင်းပြီးပါပြီ။")
    else:
        bot.send_message(chat_id, "Location ကို ခလုတ်နှိပ်ပြီးမှ ပို့ပေးပါ။")


def process_edit_photo(message):
    chat_id = message.chat.id
    if message.content_type != 'photo':
        msg = bot.send_message(chat_id, "ဓာတ်ပုံပဲ ပြန်ပို့ပေးပါ -")
        bot.register_next_step_handler(msg, process_edit_photo)
        return
    user_profiles[chat_id]['photo'] = message.photo[-1].file_id
    save_profiles()
    bot.send_message(chat_id, "✅ ဓာတ်ပုံ ပြောင်းပြီးပါပြီ။")


# ---------- VIP / KPay Flow ----------
@bot.message_handler(commands=['vip'])
def vip_info(message):
    chat_id = message.chat.id
    profile = user_profiles.get(chat_id)
    if not profile:
        bot.send_message(chat_id, "ပထမဆုံး /start နဲ့ Profile ဆောက်ပေးပါ။")
        return

    if is_vip(profile):
        bot.send_message(chat_id, "✅ သင်သည် VIP Member ဖြစ်ပြီးသားပါ — Unlimited Like ရရှိနေပါသည်။")
        return

    text = (
        f"🌟 VIP Member ({VIP_PRICE_TEXT})\n\n"
        f"VIP ဖြစ်ရင် ရရှိမည့် အကျိုးကျေးဇူးများ:\n"
        f"• Like အကန့်အသတ်မရှိ (Free user တစ်နေ့ {FREE_DAILY_LIKES} ခါသာ)\n"
        f"• ဘယ်သူတွေက Like လုပ်ထားလဲ ကြည့်နိုင်ခြင်း (/likedme)\n\n"
        f"💳 ငွေပေးချေရန် -\n"
        f"KPay/KBZPay: {KPAY_PHONE}\n"
        f"အမည်: {KPAY_NAME}\n\n"
        f"ငွေလွှဲပြီးရင် Transaction Screenshot ကို ဒီ chat ထဲ တိုက်ရိုက် ပို့ပေးပါ — "
        f"Admin စစ်ဆေးပြီး VIP ချက်ချင်း activate လုပ်ပေးပါမည်။"
    )
    bot.send_message(chat_id, text)


@bot.message_handler(content_types=['photo'])
def catch_payment_screenshot(message):
    """ဓာတ်ပုံပို့လိုက်တာက profile setup flow မှ မဟုတ်ဘဲ VIP payment proof ဖြစ်နိုင်တာကို ဖမ်းယူသည်.
    (Profile photo step ကတော့ register_next_step_handler က ဦးစားပေး ကိုင်တွယ်ပြီးသားဖြစ်၍ ဒီကို မရောက်ပါ)"""
    chat_id = message.chat.id
    profile = user_profiles.get(chat_id)
    if not profile or is_vip(profile):
        return
    try:
        bot.forward_message(ADMIN_ID, chat_id, message.message_id)
        bot.send_message(
            ADMIN_ID,
            f"💳 VIP Payment Proof\nFrom: @{profile.get('username') or chat_id} (ID: {chat_id})\n"
            f"Approve ရန်: /approve {chat_id}"
        )
        bot.send_message(chat_id, "✅ Screenshot ရရှိပါပြီ။ Admin စစ်ဆေးပြီးပါက VIP ချက်ချင်း ဖွင့်ပေးပါမည်။")
    except Exception:
        pass


@bot.message_handler(commands=['approve'])
def approve_vip(message):
    if message.chat.id != ADMIN_ID:
        return
    parts = message.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        bot.send_message(ADMIN_ID, "သုံးပုံစံ: /approve <chat_id>")
        return
    target_id = int(parts[1])
    if target_id not in user_profiles:
        bot.send_message(ADMIN_ID, "ဒီ user ကို ရှာမတွေ့ပါ။")
        return
    user_profiles[target_id]['vip'] = True
    save_profiles()
    bot.send_message(ADMIN_ID, f"✅ {target_id} ကို VIP အဖြစ် approve လုပ်ပြီးပါပြီ။")
    bot.send_message(target_id, "🎉 ကျေးဇူးတင်ပါတယ်! သင်သည် VIP Member ဖြစ်သွားပါပြီ — Unlimited Like ရရှိပါပြီ။")


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
        if prof.get('banned'):
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
        me.setdefault('blocked', []).append(target_id)
        target = user_profiles.get(target_id, {})
        target['report_count'] = target.get('report_count', 0) + 1
        if target['report_count'] >= AUTO_BAN_REPORTS:
            target['banned'] = True
        save_profiles()
        bot.answer_callback_query(call.id, "Report/Block လုပ်ပြီးပါပြီ။")

        reporter_username = me.get('username') or str(chat_id)
        target_username = target.get('username') or str(target_id)
        try:
            ban_note = "\n🚫 Auto-banned (matching list မှ ဖယ်ရှားပြီး)" if target.get('banned') else ""
            bot.send_message(
                ADMIN_ID,
                f"🚫 Report တင်ခြင်း\nReporter: @{reporter_username}\nReported user: @{target_username} (ID: {target_id})\n"
                f"စုစုပေါင်း Report ရသည့်အကြိမ်: {target['report_count']}{ban_note}"
            )
        except Exception:
            pass

        show_next_profile(chat_id)
        return

    if action == 'like':
        ensure_daily_reset(me)
        if not is_vip(me) and me.get('likes_today', 0) >= FREE_DAILY_LIKES:
            bot.answer_callback_query(
                call.id,
                f"ယနေ့အတွက် Like အကြိမ်ရေ ပြည့်သွားပါပြီ။ VIP ဖြစ်ရင် Unlimited ရပါမယ် (/vip)",
                show_alert=True
            )
            return

        me['likes_today'] = me.get('likes_today', 0) + 1
        me.setdefault('liked', []).append(target_id)
        target = user_profiles.get(target_id, {})
        target.setdefault('received_likes', []).append(chat_id)

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


# ---------- Who Liked Me (VIP only) ----------
@bot.message_handler(commands=['likedme'])
def liked_me(message):
    chat_id = message.chat.id
    profile = user_profiles.get(chat_id)
    if not profile:
        bot.send_message(chat_id, "ပထမဆုံး /start နဲ့ Profile ဆောက်ပေးပါ။")
        return
    if not is_vip(profile):
        bot.send_message(chat_id, "ဒီ Feature ကို VIP Member များသာ ကြည့်နိုင်ပါသည်။ /vip နဲ့ VIP ဖြစ်လိုက်ပါ။")
        return
    received = [uid for uid in profile.get('received_likes', []) if uid not in profile.get('liked', [])]
    if not received:
        bot.send_message(chat_id, "အခုလောလောဆယ် Like ရောက်မလာသေးပါ။")
        return
    bot.send_message(chat_id, f"❤️ သင့်ကို Like {len(received)} ယောက် လုပ်ထားပါတယ်! /find နဲ့ ပြန်ကြည့်ပါ။")


# ---------- ကိုယ့် Profile ကြည့်ခြင်း ----------
@bot.message_handler(commands=['myprofile'])
def my_profile(message):
    chat_id = message.chat.id
    if chat_id not in user_profiles or not user_profiles[chat_id].get('photo'):
        bot.send_message(chat_id, "Profile မရှိသေးပါ။ /start နဲ့ ဆောက်ပါ။")
        return
    profile = user_profiles[chat_id]
    matches = len(profile.get('matches', []))
    vip_text = "🌟 VIP Member" if is_vip(profile) else "Free Member"
    caption = (
        f"✨ Profile ✨\n👫 လိင်: {profile['gender']}\n🎂 အသက်: {profile['age']}\n"
        f"❤️ Match ရသူ: {matches} ယောက်\n👤 Status: {vip_text}"
    )
    bot.send_photo(chat_id, profile['photo'], caption=caption)


@bot.message_handler(commands=['safety'])
def safety_cmd(message):
    bot.send_message(message.chat.id, SAFETY_MESSAGE)


@bot.message_handler(commands=['help'])
def help_cmd(message):
    bot.send_message(
        message.chat.id,
        "/start - Profile အသစ်ဆောက်ရန်\n"
        "/find - အနီးအနား user ရှာရန်\n"
        "/myprofile - ကိုယ့် Profile ကြည့်ရန်\n"
        "/editprofile - Profile ပြင်ရန် / ပြန်စရန်\n"
        "/vip - VIP Member ဖြစ်ရန်\n"
        "/likedme - ဘယ်သူတွေ Like လုပ်လဲ ကြည့်ရန် (VIP)\n"
        "/safety - လုံခြုံရေး အကြံပြုချက်များ"
    )


setup_bot_commands()
print("Bot is running...")
bot.infinity_polling()
