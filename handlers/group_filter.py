# -*- coding: utf-8 -*-
"""Guruhlardagi odam yozgan buyurtmalarni avtomatik yo'lovchi kanaliga chiqaradi."""
from html import escape

from aiogram import types
from aiogram.dispatcher import FSMContext

from bot_instance import bot, dp
from config import BOT_USERNAME, DRIVER_CHANNELS, PASSENGER_CHANNELS
from keyboards import open_in_bot_kb
from keywords import KEYWORDS_RE
from storage import get_user


FILTER_GROUP_IDS = set(DRIVER_CHANNELS) | set(PASSENGER_CHANNELS)


def _profile_url(user: types.User) -> str:
    if user.username:
        return f"https://t.me/{user.username}"
    return f"tg://user?id={user.id}"


def _profile_button(user: types.User) -> types.InlineKeyboardMarkup:
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("👤 Yozgan odam profiliga o‘tish", url=_profile_url(user)))
    kb.add(InlineKeyboardButton("🤖 Botga o‘tish", url=f"https://t.me/{BOT_USERNAME}?start=zakaz"))
    return kb


@dp.message_handler(content_types=["text"], state="*")
async def group_keyword_order(message: types.Message, state: FSMContext):
    """Keyword tekshiruvini faqat odamlar yozgan guruh xabarlariga qo'llaydi."""
    if message.chat.type not in ("group", "supergroup"):
        return
    if message.chat.id not in FILTER_GROUP_IDS:
        return
    if not message.from_user or getattr(message.from_user, "is_bot", False):
        return

    text = (message.text or "").strip()
    if not text or text.startswith("/") or not KEYWORDS_RE.search(text):
        return

    sender = message.from_user
    sender_name = escape(sender.full_name or sender.username or str(sender.id))
    profile = f'<a href="{_profile_url(sender)}">{sender_name}</a>'
    saved_phone = get_user(str(sender.id)).get("phone")
    phone_line = f"\n📞 Telefon: <code>{escape(saved_phone)}</code>" if saved_phone else ""
    order_text = (
        "🚕 <b>Zakaz matni</b>\n\n"
        f"<blockquote>{escape(text)}</blockquote>\n\n"
        f"👤 Yozgan odam: {profile}{phone_line}"
    )

    delivered = False
    for destination in PASSENGER_CHANNELS:
        try:
            await bot.send_message(destination, order_text, reply_markup=_profile_button(sender))
            delivered = True
        except Exception:
            continue

    if not delivered:
        return

    try:
        await message.delete()
    except Exception:
        # Botda xabar o'chirish huquqi bo'lmasa ham, buyurtma yo'qolmaydi.
        pass

    acknowledgement = (
        f"✅ Hurmatli {profile}, zakazingiz shofyorlarimizga yuborildi.\n"
        "Shofyorlarimiz tez orada aloqaga chiqishadi. Oq yo‘l! 🚕\n\n"
        "Keyingi safar oson holda botimizdan zakaz bering."
    )
    try:
        await bot.send_message(message.chat.id, acknowledgement, reply_markup=open_in_bot_kb("zakaz"))
    except Exception:
        pass
