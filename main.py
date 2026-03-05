from core.session_manager import SessionManager
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
import json
import os
session_manager = SessionManager()
import os
import asyncio
import json
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler
from players_display import format_players_status

TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN') or os.environ.get('TOKEN')

USERS_FILE = "data/users.json"

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f)

def is_first_start(user_id):
    users = load_users()
    if str(user_id) in users:
        return False
    users[str(user_id)] = True
    save_users(users)
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if not is_first_start(user.id):
        # اگر قبلا آمده، چیزی نفرست
        return
  
   # متن خوش‌آمدگویی
    welcome_text = (
        "ورود ارزشمند شما را به @SilentWerewolfBot تبریک میگویم.\n"
        "شما با موفقیت به ربات متصل شدید.\n"
        "برای اطلاعات از خبر ها و تغییرات چنل رسمی ربات را دنبال کنید."
    )

    # دکمه‌های قابل کلیک برای آی‌دی‌ها
    keyboard = [
        [InlineKeyboardButton("کانال اخبار", url="https://t.me/silentwolfsupport")],
        [InlineKeyboardButton("ربات اصلی", url="https://t.me/SilentWerewolfBot")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup
    ) 
    
# خواندن نقش‌ها از فایل
with open("roles.json", "r", encoding="utf-8") as f:
    roles_data = json.load(f)

# ساخت دیکشنری برای دسترسی سریع به اطلاعات نقش‌ها
roles_info = {}
roles_texts = {}
for role in roles_data:
    role_name = role.get("name")
    roles_info[role_name] = role
    roles_texts[role_name] = role.get("description", "نقش شما مشخص نیست!")

# خواندن توانایی‌های شب از فایل
with open("night_abilities.json", "r", encoding="utf-8") as f:
    night_abilities = json.load(f)

# پرامپت‌های شب برای هر نقش (برای نمایش بهتر و مدیریت آسان‌تر)
night_prompts = {
    "گرگ آلفا": " به کی میخوای حمله کنی و بخوریش؟",
    "گرگ 🐺": " به کی میخوای حمله کنی و بخوریش؟",
    "گرگینه": " به کی میخوای حمله کنی و بخوریش؟",
    "توله گرگ": " به کی میخوای حمله کنی و بخوریش؟",
    "پیشگو 🔮": "🔮 استعلام چه کسی را می‌خواهی بگیری؟",
    "پیشگو": "🔮 استعلام چه کسی را می‌خواهی بگیری؟",
    "فالگیر": "🔮 استعلام چه کسی را می‌خواهی بگیری؟",
    "ساحره": "🧙‍♀️ انتخاب کن:",
    "طلسم گر": "✨ انتخاب کن:",
    "شبگرد": "🌙 انتخاب کن:",
    "جادوگر 🧙": "🧙 انتخاب کن:",
    "فرشته نگهبان": "👼 چه کسی را انتخاب می‌کنی که امشب از آن محافظت کنی؟",
    "نگهبان 🛡️": "🛡️ چه کسی را انتخاب می‌کنی که امشب از آن محافظت کنی؟",
    "قاتل فراری": "🔪 چه کسی را انتخاب می‌کنی که بکشیش؟",
    "لورد زامبی": "🧟 چه کسی را انتخاب می‌کنی که با تو هم تیم شود؟",
    "زامبی": "🧟 چه کسی را انتخاب می‌کنی که با تو هم تیم شود؟",
    "شکارچی 🏹": "🏹 چه کسی از نظر تو زامبی است؟",
    "شکارچی": "🏹 چه کسی از نظر تو زامبی است؟",
    "هیپنوتیزور": "😵‍💫 انتخاب کن:",
    "مین گذار": "💣 انتخاب کن:",
    "فاحشه": "💋 انتخاب کن:",
    "طوفان گر": "🌪️ آیا امشب می‌خواهی طوفان به‌پا کنی؟",
    "معشوق": "💘 بازیکن مورد نظر خود را انتخاب کن",
    "عاشق 💕": "💕 بازیکن مورد نظر خود را انتخاب کن",
    "پیشمرگ": "⚔️ انتخاب کن با چه کسی در ارتباط باشی (فقط شب اول)",
    "همزاد": "👥 انتخاب کن با چه کسی یکی شوی (فقط شب اول)",
}

# لیست بازیکنان برای هر مود (ذخیره username و user_id)
players = {
    "mighty": {},  # {username: user_id}
    "chaos": {},
    "cultus": {},
    "romance": {},
    "max": {}
}

# نگه داشتن پیام لیست بازیکنان برای بروزرسانی
player_list_message_id = {}

# ذخیره تسک‌های تایمر جوین برای هر مود (برای کنسل کردن یا تغییر دادن)
join_timer_tasks = {}

# ذخیره chat_id برای هر مود
mode_chat_ids = {}

# ذخیره نقش‌های توزیع شده برای هر مود
game_state = {
    "mighty": {},  # {username: role}
    "chaos": {},
    "cultus": {},
    "romance": {},
    "max": {}
}

# ذخیره وضعیت بازیکنان (زنده/مرده، اکشن شب و غیره)
player_status = {
    "mighty": {},  # {username: {"role": "...", "alive": True, "acted": False, "target": None}}
    "chaos": {},
    "cultus": {},
    "romance": {},
    "max": {}
}

# ذخیره انتخاب‌های شبانه
night_choices = {}

# نقش‌هایی که اگر تایم تموم شد، رندوم انتخاب شوند
auto_random_roles = ["پیشمرگ", "همزاد", "معشوق", "عاشق 💕"]

# تایمر شبانه (120 ثانیه)
NIGHT_DURATION = 120

# تایمر روزانه (90 ثانیه بحث + 90 ثانیه رأی‌گیری)
DAY_DISCUSSION_TIME = 90
DAY_VOTING_TIME = 90

# حداقل و حداکثر بازیکن
MIN_PLAYERS = 5
MAX_PLAYERS = 25

# تایمر بازی برای هر مود
join_times = {
    "mighty": 300,  # ۵ دقیقه
    "chaos": 300,
    "cultus": 300,
    "romance": 300,
    "max": 300
}

# متن مود
def get_mode_text(mode, user_name):
    mode_names = {
        "mighty": "قدرتی",
        "chaos": "آشوب",
        "cultus": "کاستوم",
        "romance": "عاشقانه",
        "max": "مکس"
    }
    return f"💪 حالت {mode_names[mode]} توسط {user_name} استارت شد.\n\n" \
           "می‌دونم دوس داری یه نقش با توانایی خاص داشته باشی، پس شانست رو امتحان کن!\n\n" \
           "بازیکنان با زدن دکمه زیر می‌تونن وارد روستا بشن 👇🏻"

# دکمه ورود به روستا
def get_join_keyboard(mode):
    return InlineKeyboardMarkup([[InlineKeyboardButton(" ورود به روستا🌙 ", callback_data=f"join_{mode}")]])

# متن شب
night_text = """🌌 شب آرام آرام بر روستا سایه انداخته است.
صدای زوزه ی گرگ ها🐺 از دور شنیده می‌شود. همه در خانه های خود پنهان شده اند … 
اما ترس در هوا موج میزند، اکنون زمان آن رسیده که هر کس از توانایی هایش استفاده کند.

بازیکنان شما ۱۲۰ ثانیه وقت دارین که از دکمه هایتان استفاده کنین.
شب خوش 🌙
"""

# تابع بررسی ادمین بودن کاربر
async def is_admin(context: CallbackContext, chat_id: int, user_id: int) -> bool:
    """بررسی اینکه آیا کاربر ادمین گروه است یا نه"""
    try:
        chat_member = await context.bot.get_chat_member(chat_id, user_id)
        return chat_member.status in ['creator', 'administrator']
    except Exception as e:
        print(f"خطا در بررسی ادمین: {e}")
        return False

# توزیع نقش‌ها بین بازیکنان
def build_balanced_roles(player_count):
    available_roles = list(roles_info.keys())
    negative_roles = [name for name, info in roles_info.items() if info.get("alignment") == "منفی"]
    positive_roles = [name for name, info in roles_info.items() if info.get("alignment") == "مثبت"]
    
    roles = []

    # حداقل گرگ
    if player_count <= 6:
        min_wolves = 1
    elif player_count <= 9:
        min_wolves = 2
    elif player_count <= 13:
        min_wolves = 3
    else:
        min_wolves = max(3, player_count // 4)

    # اول گرگ‌ها رو اضافه کن
    wolves_pool = [r for r in negative_roles if "گرگ" in r or r in ["گرگینه", "توله گرگ", "ساحره", "شبگرد", "طلسم گر"]]
    
    # اطمینان از وجود گرگ آلفا در صورت امکان
    if "گرگ آلفا" in wolves_pool:
        roles.append("گرگ آلفا")
        for _ in range(min_wolves - 1):
            roles.append(random.choice(wolves_pool))
    else:
        for _ in range(min_wolves):
            roles.append(random.choice(wolves_pool))

    # حالا نقش‌های مثبت
    while len(roles) < player_count:
        roles.append(random.choice(positive_roles))

    random.shuffle(roles)
    return roles

# توزیع نقش‌ها در حالت قدرتی
def build_mighty_roles(player_count):
    total_power = int(player_count * 2.5)
    negative_budget = total_power // 2
    positive_budget = total_power - negative_budget

    negative_roles = [name for name, info in roles_info.items() if info.get("alignment") == "منفی"]
    positive_roles = [name for name, info in roles_info.items() if info.get("alignment") == "مثبت"]

    roles = []
    neg_power = 0
    pos_power = 0

    # --- گرگ آلفا اجباری ---
    if "گرگ آلفا" in roles_info:
        roles.append("گرگ آلفا")
        neg_power += roles_info["گرگ آلفا"].get("weight", 5)

    # --- یک نقش اطلاعاتی قوی ---
    info_candidates = ["پیشگو", "کاراگاه", "پیشگو 🔮", "کاراگاه 🕵🏻‍♂️"]
    available_info = [r for r in info_candidates if r in roles_info]
    if available_info:
        info = random.choice(available_info)
        roles.append(info)
        pos_power += roles_info[info].get("weight", 4)

    # --- پر کردن منفی‌ها ---
    random.shuffle(negative_roles)
    for role in negative_roles:
        if role in roles: continue
        w = roles_info[role].get("weight", 3)
        if neg_power + w <= negative_budget and len(roles) < player_count:
            roles.append(role)
            neg_power += w

    # --- پر کردن مثبت‌ها ---
    random.shuffle(positive_roles)
    for role in positive_roles:
        if role in roles: continue
        w = roles_info[role].get("weight", 3)
        if pos_power + w <= positive_budget and len(roles) < player_count:
            roles.append(role)
            pos_power += w

    # --- پرکننده ---
    while len(roles) < player_count:
        roles.append("روستایی مست")

    random.shuffle(roles)
    return roles

# توزیع نقش‌ها بین بازیکنان
def assign_roles(players_list, mode="mighty"):
    if mode == "mighty":
        balanced_roles = build_mighty_roles(len(players_list))
    else:
        balanced_roles = build_balanced_roles(len(players_list))
        
    assignments = {}
    for i, player in enumerate(players_list):
        assignments[player] = balanced_roles[i]
    return assignments

# 🎭 نقش‌هایی که در شب عمل دارن
def has_night_action(role):
    return role in [
        "گرگ آلفا", "گرگ 🐺", "گرگینه", "توله گرگ", "ساحره", "شبگرد", "طلسم گر",
        "شکارچی 🏹", "شکارچی", "پیشگو 🔮", "پیشگو", "فرشته نگهبان", "نگهبان 🛡️",
        "قاتل فراری", "لورد زامبی", "زامبی", "هیپنوتیزور", "مین گذار", "فاحشه",
        "فالگیر", "پیشمرگ", "همزاد", "طوفان گر", "معشوق", "عاشق 💕", "جادوگر 🧙"
    ]

# ارسال نقش‌ها در پیوی
async def send_roles(context: CallbackContext, assignments, players_dict):
    for username, role in assignments.items():
        try:
            user_id = players_dict.get(username)
            if user_id:
                role_description = roles_texts.get(role, "نقش شما مشخص نیست!")
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f" نقشت  : {role}\n\n{role_description}"
                )
        except Exception as e:
            print(f"خطا در ارسال نقش به {username}: {e}")

# ارسال توانایی شب به بازیکن (بهبود یافته)
async def send_night_ability(context: CallbackContext, username, user_id, role, players_list):
    """ارسال پیام توانایی شب به پیوی بازیکن با دکمه‌های انتخاب"""
    
    # اگر نقش توانایی شب ندارد، برگرد
    if not has_night_action(role):
        return
    
    # متن پیام از دیکشنری پرامپت‌ها (با fallback به night_abilities.json)
    prompt_text = night_prompts.get(role) or night_abilities.get(role) or "انتخاب خود را انجام بده:"
    
    # ساخت دکمه‌ها بر اساس نوع نقش
    buttons = []
    
    if role == "طوفان گر":
        # دکمه بله/خیر برای طوفان گر
        buttons = [
            [InlineKeyboardButton("✅ بله", callback_data=f"night_{username}_yes")],
            [InlineKeyboardButton("❌ خیر", callback_data=f"night_{username}_no")]
        ]
    else:
        # دکمه‌های انتخاب بازیکن برای بقیه نقش‌ها
        buttons = [
            [InlineKeyboardButton(player_name, callback_data=f"night_{username}_{player_name}")]
            for player_name in players_list 
            if player_name != username
        ]
    
    # ارسال پیام با دکمه‌ها
    await context.bot.send_message(
        chat_id=user_id,
        text=prompt_text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# 🔄 تبدیل قربانی به گرگ یا زامبی
def try_conversion(victim, attacker_role):
    """
    بررسی احتمال تبدیل قربانی به گرگ یا زامبی
    victim: شیء بازیکن هدف
    attacker_role: نقش حمله‌کننده (مثلاً گرگ آلفا یا زامبی)
    """
    victim_role = victim.get("role")
    victim_role_info = roles_info.get(victim_role)
    
    if not victim_role_info:
        return None  # نقش قربانی پیدا نشد
    
    # 🐺 حمله توسط گرگ آلفا
    if attacker_role == "گرگ آلفا":
        chance = victim_role_info.get("wolf_conversion_chance", 0)
        if random.randint(1, 100) <= chance:
            victim["team"] = "گرگ‌ها"
            victim["role"] = "گرگینه"
            return "wolf_converted"
    
    # 🧟 حمله توسط زامبی
    elif attacker_role == "زامبی":
        chance = victim_role_info.get("zombie_infection_chance", 0)
        if random.randint(1, 100) <= chance:
            victim["team"] = "زامبی‌ها"
            victim["role"] = "زامبی"
            return "zombie_converted"
    
    return None

# 📜 ارسال لیست بازیکنان زنده/مرده
async def send_alive_list(context: CallbackContext, mode: str, chat_id):
    status = player_status[mode]
    if not status:
        return
    
    players_alive = []
    players_dead = []
    
    for username, p in status.items():
        user_id = players[mode].get(username)
        player_data = {'name': username, 'id': user_id}
        
        if p["alive"]:
            players_alive.append(player_data)
        else:
            player_data['role'] = p['role']
            player_data['result'] = 'باخت'
            players_dead.append(player_data)
    
    text = format_players_status(players_alive, players_dead)
    await context.bot.send_message(chat_id, text, parse_mode="Markdown")

# 💀 اعمال اتفاق‌های شب (مرگ‌ها، بررسی پیشگو، محافظت و غیره)
async def resolve_night_actions(context: CallbackContext, mode: str, chat_id):
    status = player_status[mode]
    dead_players = []
    report = "🕯 عملیات شب:\n"

    # شبیه‌سازی حمله گرگ‌ها
    wolf_roles = ["گرگ آلفا", "گرگ 🐺", "گرگینه", "توله گرگ"]
    wolves = [
        (username, p) for username, p in status.items()
        if p["alive"] and p["role"] in wolf_roles
    ]
    
    # بررسی نقره‌پاشی آهنگر
    silver_night = game_state.get(mode, {}).get("silver_night_active", False)
    if silver_night:
        report += "⚒ آهنگر دیشب نقره‌پاشی کرده بود، گرگ‌ها نتوانستند حمله کنند! ✨\n"
        # ریست کردن وضعیت برای شب بعد
        game_state[mode]["silver_night_active"] = False
    elif wolves:
        all_targets = [p["target"] for _, p in wolves if p["target"]]
        if all_targets:
            # انتخاب هدف با بیشترین رأی
            from collections import Counter
            target_counts = Counter(all_targets)
            victim_username = target_counts.most_common(1)[0][0]
            
            if status[victim_username]["alive"]:
                # بررسی وجود گرگ آلفا
                has_alpha = any(p["role"] == "گرگ آلفا" for _, p in wolves)
                
                # سعی برای تبدیل (فقط اگر گرگ آلفا باشد)
                conversion_result = None
                if has_alpha:
                    conversion_result = try_conversion(status[victim_username], "گرگ آلفا")
                
                if conversion_result == "wolf_converted":
                    report += f"😱 {victim_username} توسط گرگ آلفا گاز گرفته شد و به گرگینه تبدیل شد! 🐺\n"
                    # ارسال پیام به بازیکن تبدیل شده
                    user_id = players[mode].get(victim_username)
                    if user_id:
                        try:
                            await context.bot.send_message(
                                chat_id=user_id,
                                text=f"🐺 تبدیل شدی! نقش جدید شما: گرگینه\n\nاکنون با تیم گرگ‌ها هستی!"
                            )
                        except:
                            pass
                else:
                    # اگر تبدیل نشد، کشته می‌شود
                    status[victim_username]["alive"] = False
                    dead_players.append(victim_username)
                    report += f"☠️ {victim_username} در شب توسط گرگ‌ها کشته شد...\n"

    # شبیه‌سازی حمله زامبی‌ها
    zombie_roles = ["لورد زامبی", "زامبی"]
    zombies = [
        (username, p) for username, p in status.items()
        if p["alive"] and p["role"] in zombie_roles
    ]
    
    for zombie_username, zombie_data in zombies:
        if zombie_data.get("target"):
            target_username = zombie_data["target"]
            if status[target_username]["alive"]:
                conversion_result = try_conversion(status[target_username], "زامبی")
                
                if conversion_result == "zombie_converted":
                    report += f"💀 {target_username} آلوده شد و حالا یکی از زامبی‌هاست! 🧟\n"
                    # ارسال پیام به بازیکن تبدیل شده
                    user_id = players[mode].get(target_username)
                    if user_id:
                        try:
                            await context.bot.send_message(
                                chat_id=user_id,
                                text=f"🧟 تبدیل شدی! نقش جدید شما: زامبی\n\nاکنون با تیم زامبی‌ها هستی!"
                            )
                        except:
                            pass

    # شبیه‌سازی استعلام پیشگو
    seer_roles = ["پیشگو 🔮", "پیشگو"]
    seers = [
        (username, p) for username, p in status.items()
        if p["alive"] and p["role"] in seer_roles
    ]
    
    # مدیریت پیشمرگ (Sacrifice)
    sacrifice_mapping = {} # {master: sacrifice_username}
    for username, p in status.items():
        if p["alive"] and p["role"] == "پیشمرگ ⚰️" and p.get("target"):
            sacrifice_mapping[p["target"]] = username

    # اعمال مرگ‌ها با در نظر گرفتن پیشمرگ
    final_dead_players = []
    for victim in dead_players:
        if victim in sacrifice_mapping:
            sacrifice_name = sacrifice_mapping[victim]
            if status[sacrifice_name]["alive"]:
                status[sacrifice_name]["alive"] = False
                final_dead_players.append(sacrifice_name)
                report += f"🛡️ پیشمرگ ({sacrifice_name}) جان خود را فدای {victim} کرد و به جای او کشته شد! ⚰️\n"
                continue
        final_dead_players.append(victim)

    for username, s in seers:
        if s["target"]:
            target_role = status[s["target"]]["role"]
            # ارسال پیام خصوصی به پیشگو
            user_id = players[mode].get(username)
            if user_id:
                try:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=f"🔮 استعلام شما: {s['target']} نقش {target_role} را دارد."
                    )
                except:
                    pass

    if not dead_players:
        report += "- در شب گذشته هیچ اتفافی نیوفتاد همه به خونه هاتون بگردید . 🌙\n"

    await start_day_phase(context, mode, chat_id, report)

# 🔘 ارسال دکمه‌های اکشن اختصاصی
async def send_action_buttons(context: CallbackContext, chat_id: int, player_id: int, role_info: dict, mode: str):
    """ارسال دکمه‌های اکشن بر اساس ساختار ارسالی کاربر"""
    status = player_status[mode]
    players_dict = players[mode]
    
    # پیدا کردن نام کاربری بازیکن فرستنده
    sender_username = None
    for uname, uid in players_dict.items():
        if uid == player_id:
            sender_username = uname
            break
            
    if not sender_username:
        return

    buttons = []
    actions = role_info.get("actions", [])
    
    for action in actions:
        if action.get("target") == "player":
            for target_username, p_data in status.items():
                if not p_data["alive"]:
                    continue
                if players_dict.get(target_username) == player_id:
                    continue
                
                # فرمت callback_data: actionKey:senderId:targetUsername
                # نکته: در تلگرام محدودیت کاراکتر برای callback_data وجود دارد (64 بایت)
                # از username استفاده می‌کنیم چون در این بات کلید اصلی است
                callback_data = f"act:{action['key']}:{target_username}"
                buttons.append([InlineKeyboardButton(
                    text=f"{action['button']} ➜ {target_username}",
                    callback_data=callback_data
                )])
        
        elif action.get("target") == "none":
            callback_data = f"act:{action['key']}:none"
            buttons.append([InlineKeyboardButton(
                text=action["button"],
                callback_data=callback_data
            )])

    if buttons:
        try:
            await context.bot.send_message(
                chat_id=player_id,
                text="🔘 نوبت استفاده از توانایی شماست:",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        except Exception as e:
            print(f"Error sending action buttons: {e}")

# 🌞 ارسال دکمه‌های روز
async def send_day_buttons(context: CallbackContext, mode: str, chat_id: int):
    status = player_status[mode]
    players_dict = players[mode]
    
    for username, p in status.items():
        if not p["alive"]:
            continue
            
        role_name = p["role"]
        role_info = roles_info.get(role_name)
        
        if not role_info:
            continue
            
        # بررسی فاز روز و وجود اکشن‌ها
        if role_info.get("phase") == "day" and role_info.get("actions"):
            user_id = players_dict.get(username)
            if user_id:
                await send_action_buttons(context, chat_id, user_id, role_info, mode)
        
        # منطق قدیمی برای پاور تایپ روزانه (برای سازگاری)
        elif role_info.get("power_type") and "روزانه" in role_info["power_type"]:
            user_id = players_dict.get(username)
            if user_id:
                try:
                    players_list = [name for name, data in status.items() if data["alive"] and name != username]
                    buttons = [[InlineKeyboardButton(target, callback_data=f"day_{username}_{target}")] for target in players_list]
                    if buttons:
                        await context.bot.send_message(chat_id=user_id, text=f"☀️ نوبت روز شماست! {role_name} عزیز، انتخاب کن:", reply_markup=InlineKeyboardMarkup(buttons))
                except: pass

# 🌞 شروع فاز روز
async def start_day_phase(context: CallbackContext, mode: str, chat_id, report):
    text = (
        f"{report}\n"
        "همه بازیکن‌ها 120 ثانیه وقت دارین که منفی‌های بازی رو پیدا کنین "
        "و آن‌ها را از بازی خارج کنین.\n"
        "🌻 روز خوش!\n"
    )

    await context.bot.send_message(
        chat_id=chat_id,
        text=text
    )
    
    # ارسال دکمه‌های اکشن روزانه برای نقش‌های واجد شرایط
    await send_day_buttons(context, mode, chat_id)

# تایمر شبانه
async def start_night_timer(context: CallbackContext, mode: str, chat_id):
    """تایمر شبانه با بررسی اتمام زودتر اگر همه عمل کردند"""
    remaining = NIGHT_DURATION
    check_interval = 5  # هر 5 ثانیه بررسی کن
    elapsed = 0
    
    while remaining > 0:
        # بررسی کن آیا همه بازیکنان با توانایی شب، عمل کردند؟
        status = player_status[mode]
        all_acted = all(
            (not p["alive"]) or 
            (not has_night_action(p["role"])) or 
            p["acted"]
            for p in status.values()
        )
        
        if all_acted:
        
            break
    
    # پایان شب - انتخاب رندوم برای نقش‌های خاص که عمل نکردند
    status = player_status[mode]
    players_list = list(players[mode].keys())
    
    for username, p in status.items():
        if p["alive"] and p["role"] in auto_random_roles and not p["acted"]:
            choice = random.choice([u for u in players_list if u != username and status[u]["alive"]])
            p["target"] = choice
            p["acted"] = True
            
            user_id = players[mode].get(username)
            if user_id:
                try:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=f"خب خب تایم انتخابت تموم شد و خودم برایت {choice} را انتخاب کردم"
                    )
                except:
                    pass
    
    # اعمال اتفاقات شب
    await resolve_night_actions(context, mode, chat_id)

# تابع شروع بازی با پیام شب
async def start_game_with_night(context: CallbackContext, mode: str, chat_id):
    players_dict = players[mode]
    players_list = list(players_dict.keys())
    
    if len(players_list) < 3:  # حداقل تعداد بازیکن
        await context.bot.send_message(chat_id=chat_id, text="تعداد بازیکنان کافی نیست!")
        return

    # توزیع نقش‌ها از فایل JSON
    assignments = assign_roles(players_list, mode=mode)
    game_state[mode] = assignments  # ذخیره نقش‌ها
    
    # ایجاد وضعیت بازیکنان
    player_status[mode] = {
        username: {
            "role": role,
            "alive": True,
            "acted": False,
            "target": None
        }
        for username, role in assignments.items()
    }

    # ارسال نقش‌ها در پیوی
    await send_roles(context, assignments, players_dict)

    # ارسال پیام شب در گروه
    await context.bot.send_message(chat_id=chat_id, text=night_text)
    
    # ارسال لیست بازیکنان زنده
    await send_alive_list(context, mode, chat_id)
    
    # ارسال توانایی‌های شب به همه بازیکنان
    for username, role in assignments.items():
        user_id = players_dict.get(username)
        if user_id:
            await send_night_ability(context, username, user_id, role, players_list)
    
    # شروع تایمر شب
    asyncio.create_task(start_night_timer(context, mode, chat_id))

# ابتدای main.py، قبل از هر تابع   
timer_message_id = {} # ذخیره message_id پیام تایمر برای هر chat_id

# تایمر جوین (پیام تایمر با دکمه ورود)
async def start_join_timer(context: CallbackContext, chat_id, mode):
    total_time = join_times[mode]  # 300 ثانیه = 5 دقیقه
    interval = 45  # هر 45 ثانیه یک بار پیام بده 
    
    pass
   
async def join_timer_loop(context: CallbackContext, mode: str, chat_id: int):
    total_time = 120  # تایمر کل جوین (مثال: 2 دقیقه)
    interval = 5       # هر چند ثانیه پیام بروزرسانی شود

    while total_time > 45:  # حلقه تا 45 ثانیه قبل از شروع بازی
        await asyncio.sleep(interval)
        total_time -= interval
        join_times[mode] = total_time  # بروزرسانی زمان باقیمانده

        minutes = total_time // 60
        seconds = total_time % 60

        # پاک کردن پیام قبلی تایمر اگر وجود دارد
        if chat_id in timer_message_id:
            try:
                await context.bot.delete_message(
                    chat_id=chat_id,
                    message_id=timer_message_id[chat_id]
                )
            except:
                pass

        # ارسال پیام تایمر جدید با دکمه ورود به روستا
        timer_msg = await context.bot.send_message(
            chat_id=chat_id,
            text=f"⏳ {minutes} دقیقه و {seconds} ثانیه تا شروع بازی مونده!",
            reply_markup=get_join_keyboard(mode)  # دکمه ورود
        )

        # ذخیره message_id برای پاک کردن در بار بعد
        timer_message_id[chat_id] = timer_msg.message_id

# ------------------------------------------
# فراخوانی هنگام شروع بازی یا تعداد ناکافی
async def cleanup_join_timer(context: CallbackContext, chat_id: int):
    if chat_id in timer_message_id:
        try:
            await context.bot.delete_message(
                chat_id=chat_id,
                message_id=timer_message_id[chat_id]
            )
        except:
            pass
        del timer_message_id[chat_id]
            
            # صبر تا پایان تایمر
            await asyncio.sleep(45)
        
        # بررسی تعداد بازیکنان
        players_count = len(players[mode])
        
        if players_count >= MIN_PLAYERS:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"✅ بازی با موفقیت شروع شد! ({players_count} بازیکن)"
            )
            # شروع بازی با فاز شب
            await start_game_with_night(context, mode, chat_id)
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"❌ خب خب رفقا، تعدادتون به حد نصاب نرسید ({players_count}/{MIN_PLAYERS}) و بازی شروع نشد."
            )
            # پاک کردن لیست بازیکنان
            players[mode].clear()
    except asyncio.CancelledError:
        # تایمر کنسل شد (مثلاً با /begin)
        pass
    finally:
        # پاک کردن تسک از دیکشنری
        if mode in join_timer_tasks:
            del join_timer_tasks[mode]

# شروع مود
async def start_mode(update: Update, context: CallbackContext, mode: str):
    if not update.effective_chat or not update.effective_user:
        return
        
    chat_id = update.effective_chat.id
    user_name = update.effective_user.username or update.effective_user.first_name

    # بررسی اینکه بازی قبلاً شروع شده یا نه
    if mode in join_timer_tasks:
        await update.message.reply_text("یک بازی در این مود در حال اجراست ❗️")
        return

    # ذخیره chat_id برای این مود
    mode_chat_ids[mode] = chat_id

    # پیام متن مود با دکمه ورود
    text = get_mode_text(mode, user_name)
    await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=get_join_keyboard(mode))

    # پیام لیست بازیکنان جدا
    msg = await context.bot.send_message(chat_id=chat_id, text=f"#Players: 0/{MAX_PLAYERS}\n")
    player_list_message_id[mode] = msg.message_id

    # شروع تایمر جوین در background و ذخیره تسک
    task = asyncio.create_task(start_join_timer(context, chat_id, mode))
    join_timer_tasks[mode] = task

# دستورات مودها
async def start_mighty(update: Update, context: CallbackContext):
    await start_mode(update, context, "mighty")

async def start_chaos(update: Update, context: CallbackContext):
    await start_mode(update, context, "chaos")

async def start_cultus(update: Update, context: CallbackContext):
    await start_mode(update, context, "cultus")

async def start_romance(update: Update, context: CallbackContext):
    await start_mode(update, context, "romance")

async def start_max(update: Update, context: CallbackContext):
    await start_mode(update, context, "max")

# دستور /extend برای تغییر تایم جوین (فقط ادمین)
async def extend_time(update: Update, context: CallbackContext):
    """اضافه یا کم کردن زمان جوین"""
    if not update.effective_chat or not update.effective_user:
        return
    
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    # بررسی ادمین بودن
    if not await is_admin(context, chat_id, user_id):
        await update.message.reply_text("⚠️ فقط ادمین‌ها می‌تونن زمان رو تغییر بدن!")
        return
    
    # پیدا کردن مودی که در این چت در حال اجراست
    mode = None
    for m, cid in mode_chat_ids.items():
        if cid == chat_id and m in join_timer_tasks:
            mode = m
            break
    
    if not mode:
        await update.message.reply_text("هنوز بازی‌ای شروع نشده یا بازی قبلاً آغاز شده است ❗️")
        return
    
    # خواندن مقدار تغییر از دستور
    change = 30  # مقدار پیش‌فرض
    
    if context.args and len(context.args) > 0:
        try:
            change = int(context.args[0])
        except ValueError:
            await update.message.reply_text("لطفاً عدد درست وارد کن 🔢\nمثال: /extend 60")
            return
    
    # محدودیت بین -300 تا +300
    if change > 300:
        change = 300
    elif change < -300:
        change = -300
    
    # تغییر زمان
    join_times[mode] += change
    if join_times[mode] < 0:
        join_times[mode] = 0
    
    minutes = join_times[mode] // 60
    seconds = join_times[mode] % 60
    
    await update.message.reply_text(
        f"⏱ {abs(change)} ثانیه {'اضافه' if change > 0 else 'کم'} شد.\n"
        f"الان {minutes} دقیقه و {seconds} ثانیه برای جوین شدن فرصت دارید."
    )

# دستور /begin برای شروع سریع بازی (فقط ادمین)
async def begin_game(update: Update, context: CallbackContext):
    """شروع فوری بازی بدون انتظار برای تایمر"""
    if not update.effective_chat or not update.effective_user:
        return
    
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    # بررسی ادمین بودن
    if not await is_admin(context, chat_id, user_id):
        await update.message.reply_text("⚠️ فقط ادمین می‌تونه بازی رو شروع کنه.")
        return
    
    # پیدا کردن مودی که در این چت در حال اجراست
    mode = None
    for m, cid in mode_chat_ids.items():
        if cid == chat_id and m in join_timer_tasks:
            mode = m
            break
    
    if not mode:
        await update.message.reply_text("بازی‌ای برای شروع وجود نداره ❗️")
        return
    
    # بررسی تعداد بازیکنان
    players_count = len(players[mode])
    if players_count < MIN_PLAYERS:
        await update.message.reply_text(
            f"❌ تعداد بازیکنان کافی نیست! حداقل {MIN_PLAYERS} بازیکن لازم است.\n"
            f"الان فقط {players_count} بازیکن وارد شده."
        )
        return
    
    # کنسل کردن تایمر
    if mode in join_timer_tasks:
        join_timer_tasks[mode].cancel()
    
    # شروع بازی
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"✅ بازی با دستور ادمین شروع شد! ({players_count} بازیکن)"
    )
    await start_game_with_night(context, mode, chat_id)

# دستور /cancelgame برای لغو بازی (فقط ادمین)
async def cancel_game(update: Update, context: CallbackContext):
    """لغو کردن بازی در حال اجرا"""
    if not update.effective_chat or not update.effective_user:
        return
    
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    # بررسی ادمین بودن
    if not await is_admin(context, chat_id, user_id):
        await update.message.reply_text("⚠️ فقط ادمین می‌تونه بازی رو لغو کنه.")
        return
    
    # پیدا کردن مودی که در این چت در حال اجراست
    mode = None
    for m, cid in mode_chat_ids.items():
        if cid == chat_id:
            mode = m
            break
    
    if not mode:
        await update.message.reply_text("هیچ بازی‌ای برای لغو وجود نداره.")
        return
    
    # کنسل کردن تایمر اگر در حال اجراست
    if mode in join_timer_tasks:
        join_timer_tasks[mode].cancel()
        del join_timer_tasks[mode]
    
    # پاک کردن اطلاعات بازی
    players[mode].clear()
    game_state[mode].clear()
    player_status[mode].clear()
    if mode in mode_chat_ids:
        del mode_chat_ids[mode]
    if mode in player_list_message_id:
        del player_list_message_id[mode]
    
    # ریست کردن تایم به پیش‌فرض
    join_times[mode] = 300
    
    await update.message.reply_text("❌ بازی لغو شد و از نو می‌تونید شروع کنید.")

# پردازش اکشن‌های داینامیک (جدید)
async def handle_dynamic_action(query, data):
    """پردازش اکشن‌های تعریف شده در فیلد actions نقش‌ها"""
    # فرمت: act:actionKey:targetUsername
    parts = data.split(":")
    if len(parts) < 3:
        return
    
    action_key = parts[1]
    target_username = parts[2]
    user_id = query.from_user.id
    username = query.from_user.username or query.from_user.first_name

    # پیدا کردن مود
    mode = None
    for m in ["mighty", "chaos", "cultus", "romance", "max"]:
        if username in player_status.get(m, {}):
            mode = m
            break
            
    if not mode:
        await query.answer("خطا: بازی یافت نشد!")
        return

    # ذخیره اکشن
    player_status[mode][username]["last_action"] = {
        "key": action_key,
        "target": target_username,
        "time": "day" # یا بر اساس فاز فعلی
    }
    
    # منطق اختصاصی آهنگر (نقره‌پاشی)
    if action_key == "silver_night":
        player_status[mode][username]["silver_night_used"] = True
        # این متغیر در resolve_night_actions چک می‌شود تا جلوی حمله گرگ‌ها را بگیرد
        game_state[mode]["silver_night_active"] = True
    
    await query.edit_message_text(f"✅ توانایی '{action_key}' با موفقیت روی {target_username} استفاده شد.")
    await query.answer("ثبت شد!")

# پردازش انتخاب‌های روزانه (جدید)
async def handle_day_choice(query, data):
    """پردازش انتخاب روزانه بازیکن"""
    parts = data.split("_", 2)
    if len(parts) < 3:
        return
    
    username = parts[1]
    target = parts[2]
    
    # پیدا کردن مود بازیکن
    mode = None
    for m in ["mighty", "chaos", "cultus", "romance", "max"]:
        if username in player_status.get(m, {}):
            mode = m
            break
    
    if not mode or username not in player_status[mode]:
        await query.answer("❌ خطا در پردازش انتخاب!")
        return
    
    # ذخیره انتخاب روزانه (می‌تونیم در فیلد جدیدی ذخیره کنیم یا فعلاً در همان target)
    # برای جلوگیری از تداخل با شب، بهتر است فیلد جداگانه باشد اما فعلاً ساده نگه می‌داریم
    player_status[mode][username]["day_target"] = target
    player_status[mode][username]["day_acted"] = True
    
    # متن تایید
    role_name = player_status[mode][username]["role"]
    confirmation_text = f"☀️ {role_name} عزیز، انتخاب شما برای امروز ثبت شد: {target}"
    await query.edit_message_text(text=confirmation_text)
    await query.answer("✅ انتخاب روزانه ثبت شد!")

# پردازش انتخاب‌های شبانه (بهبود یافته)
async def handle_night_choice(query, data):
    """پردازش انتخاب شبانه بازیکن"""
    parts = data.split("_", 2)  # تقسیم فقط از اولین 2 underscore
    if len(parts) < 3:
        return
    
    username = parts[1]
    choice = parts[2]  # نام بازیکن انتخاب شده یا yes/no
    
    # پیدا کردن مود بازیکن
    mode = None
    for m in ["mighty", "chaos", "cultus", "romance", "max"]:
        if username in player_status.get(m, {}):
            mode = m
            break
    
    if not mode or username not in player_status[mode]:
        await query.answer("❌ خطا در پردازش انتخاب!")
        return
    
    # ذخیره انتخاب
    player_status[mode][username]["target"] = choice
    player_status[mode][username]["acted"] = True
    
    # بروزرسانی پیام
    confirmation_text = f"✅ انتخاب صادر شد. نام انتخاب‌شونده: {choice}"
    await query.edit_message_text(text=confirmation_text)
    await query.answer("✅ انتخاب ثبت شد!")

# پردازش ورود بازیکن به بازی
async def handle_join(query, context, data):
    """پردازش درخواست ورود بازیکن به بازی"""
    mode = data.split("_")[1]
    user = query.from_user
    user_id = user.id
    user_name = user.first_name
    
    # بررسی اینکه بازیکن قبلاً وارد شده یا نه
    if user_id in players[mode]:
        await query.answer("شما قبلاً وارد شده‌اید!")
        return
    
    # بررسی حداکثر تعداد بازیکنان
    if len(players[mode]) >= MAX_PLAYERS:
        await query.answer("❌ متأسفانه ظرفیت بازی پر شده است!", show_alert=True)
        return
    
    # اضافه کردن بازیکن
    players[mode][user_id] = {
    "name": user_name 
}
    await query.answer(f"✅ شما با موفقیت وارد شدید! ({len(players[mode])}/{MAX_PLAYERS})")
    
    # بروزرسانی لیست بازیکنان
    chat_id = query.message.chat.id if query.message.chat else None
    msg_id = player_list_message_id.get(mode)
    
    # ارسال پیام ورود بازیکن با ID
    if chat_id:
        await context.bot.send_message(
            chat_id=chat_id,
            text = f'<a href="tg://user?id={user_id}">{user_name}</a>\nچند لحظه پیش وارد بازی شد ✅',
            parse_mode="HTML"
        )
    
    if msg_id and chat_id:
        player_list = "\n".join(
            [f"{i+1}. <a href='tg://user?id={uid}'>{data['name']}</a>"
             for i, (uid, data) in enumerate(players[mode].items())]
        )
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=msg_id,
            text=f"#Players: {len(players[mode])}\n{player_list}",
            parse_mode="HTML"
        )

# هندلر اصلی دکمه‌ها (ساده‌شده)
async def button(update: Update, context: CallbackContext):
    """هندلر اصلی برای تمام callback queryها"""
    query = update.callback_query
    
    if not query or not query.data:
        return
    
    data = query.data
    
    # مسیریابی به هندلر مناسب
    if data.startswith("night_"):
        await handle_night_choice(query, data)
    elif data.startswith("day_"):
        await handle_day_choice(query, data)
    elif data.startswith("act:"):
        await handle_dynamic_action(query, data)
    elif data.startswith("join_"):
        await handle_join(query, context, data)

def main():
    if not TOKEN:
        print("خطا: توکن ربات تنظیم نشده است!")
        return

    # ساخت اپلیکیشن
    application = Application.builder().token(TOKEN).build()

    # اضافه کردن هندلر start
    application.add_handler(CommandHandler("start", start))

    # ثبت دستورات مودها
    application.add_handler(CommandHandler("startmighty", start_mighty))
    application.add_handler(CommandHandler("startchaos", start_chaos))
    application.add_handler(CommandHandler("startcultus", start_cultus))
    application.add_handler(CommandHandler("startromance", start_romance))
    application.add_handler(CommandHandler("startmax", start_max))
    
    # دستورات کنترل بازی
    application.add_handler(CommandHandler("extend", extend_time))
    application.add_handler(CommandHandler("begin", begin_game))
    application.add_handler(CommandHandler("cancelgame", cancel_game))

    # دکمه‌ها
    application.add_handler(CallbackQueryHandler(button))

    # شروع ربات
    print("ربات بازی در حال اجرا است...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
