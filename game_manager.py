from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# ====== مرحله رأی‌گیری ======
async def voting_phase(chat_id):
    game = games.get(chat_id)
    if not game:
        return

    vote_text = (
        "🏞️ خب خب همه جمع بشین که موقع حذف یکی از بازیکنان رسیده.\n\n"
        "شما ۹۰ ثانیه وقت دارین تا به کسی که میخواین اجماع شه، رأی بدین."
    )

    # ساخت دکمه برای هر بازیکن زنده
    buttons = []
    for pid, name in game["players"].items():
        buttons.append([InlineKeyboardButton(text=name, callback_data=f"vote_{pid}")])

    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    game["votes"] = {}
    await bot.send_message(chat_id, vote_text, reply_markup=markup)

    # ۹۰ ثانیه برای رأی دادن
    await asyncio.sleep(90)
    await end_voting(chat_id)


# ====== وقتی بازیکن رأی می‌دهد ======
@dp.callback_query_handler(lambda c: c.data.startswith("vote_"))
async def handle_vote(callback_query: types.CallbackQuery):
    chat_id = callback_query.message.chat.id
    voter_id = callback_query.from_user.id
    target_id = callback_query.data.split("_")[1]

    game = games.get(chat_id)
    if not game or game["status"] != "started":
        return

    if voter_id not in game["players"]:
        await callback_query.answer("شما در این بازی نیستید ❌", show_alert=True)
        return

    # ثبت رأی بازیکن
    game["votes"][voter_id] = target_id
    target_name = game["players"].get(int(target_id), "بازیکن ناشناس")

    await bot.send_message(chat_id, f"📣 {game['players'][voter_id]} رأی خودش رو به {target_name} داد تا به چوبه‌دار آویخته بشه.")
    await callback_query.answer("رأی شما ثبت شد ✅")


# ====== پایان رأی‌گیری ======
async def end_voting(chat_id):
    game = games.get(chat_id)
    if not game or game["status"] != "started":
        return

    # شمارش آرا
    vote_counts = {}
    for target in game["votes"].values():
        vote_counts[target] = vote_counts.get(target, 0) + 1

    if not vote_counts:
        await bot.send_message(chat_id, "😶 کسی رأی نداد، روستا در سردرگمی موند!")
        await start_night_phase(chat_id)
        return

    # پیدا کردن بیشترین رأی
    max_votes = max(vote_counts.values())
    candidates = [uid for uid, count in vote_counts.items() if count == max_votes]
    executed_id = int(random.choice(candidates))
    executed_name = game["players"][executed_id]
    executed_role = game["roles"].get(executed_id, "نقش نامشخص")

    # حذف بازیکن
    del game["players"][executed_id]

    msg = (
        f"⚖️ رأی‌گیری تموم شد و بر حسب رأی‌های مردمی {executed_name} به چوبه‌دار آویخته شد.\n"
        f"خب … چیزی نبود جز یه {executed_role} 💀\n\n"
        "🌌 شب بر روستا سایه انداخته است...\n"
        "بعد از یه روز پرماجرا، روستایی‌ها میرن خونشون و امیدوارن اتفاقی نیفته.\n\n"
        "بازیکن‌ها! شما ۹۰ ثانیه وقت دارین که از دکمه‌هاتون استفاده کنین.\n"
        "🌙 شب خوش"
    )
    await bot.send_message(chat_id, msg)

    # ۹۰ ثانیه صبر → صبح بعدی
    await asyncio.sleep(90)
    await morning_phase(chat_id) 
from random import randint
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# ====== دکمه‌های مخصوص نقش گرگ آلفا ======
async def wolf_alpha_night(chat_id, wolf_id):
    game = games.get(chat_id)
    if not game:
        return

    # فقط اگر گرگ زنده باشه
    if wolf_id not in game["players"]:
        return

    buttons = []
    for pid, name in game["players"].items():
        if pid != wolf_id:  # خودش رو هدف نگیره
            buttons.append([InlineKeyboardButton(text=name, callback_data=f"wolfattack_{wolf_id}_{pid}")])

    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.send_message(
        wolf_id,
        "🌑 شب فرارسیده، گرگ آلفا!\nیکی از قربانیان رو انتخاب کن تا پاره‌اش کنی 😈👇",
        reply_markup=markup
    )


# ====== وقتی گرگ آلفا هدفش رو انتخاب می‌کنه ======
@dp.callback_query_handler(lambda c: c.data.startswith("wolfattack_"))
async def handle_wolf_attack(callback_query: types.CallbackQuery):
    _, wolf_id, target_id = callback_query.data.split("_")
    wolf_id = int(wolf_id)
    target_id = int(target_id)
    chat_id = None

    # پیدا کردن بازی فعال
    for cid, game in games.items():
        if wolf_id in game["players"]:
            chat_id = cid
            break

    if not chat_id:
        return

    game = games.get(chat_id)
    if not game:
        return

    attacker_name = game["players"].get(wolf_id, "گرگ ناشناس")
    target_name = game["players"].get(target_id, "قربانی نامشخص")

    # ثبت هدف حمله
    game["wolf_target"] = target_id

    await bot.send_message(wolf_id, f"🎯 هدف تو برای حمله امشب: {target_name}")
    await callback_query.answer("هدف ثبت شد ✅")


# ====== اجرای حمله گرگ‌ها ======
async def process_wolf_attack(chat_id):
    game = games.get(chat_id)
    if not game or "wolf_target" not in game:
        return

    target_id = game["wolf_target"]
    if target_id not in game["players"]:
        return

    target_name = game["players"][target_id]

    # احتمال ۲۰٪ تبدیل به گرگ
    if randint(1, 100) <= 20:
        game["roles"][target_id] = "گرگینه 🐺"
        msg = f"😈 {target_name} توسط گرگ آلفا گاز گرفته شد و حالا خودش یک گرگینه است!"
    else:
        del game["players"][target_id]
        msg = f"🩸 {target_name} دیشب طعمه گرگ آلفا شد و از بازی حذف گردید!"

    await bot.send_message(chat_id, msg)
    game.pop("wolf_target", None)