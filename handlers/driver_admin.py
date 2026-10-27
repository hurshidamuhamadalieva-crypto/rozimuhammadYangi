# -*- coding: utf-8 -*-
"""
handlers/driver_admin.py — haydovchilik arizalarini admin tomonidan
tasdiqlash/rad etish va tasdiqlangan haydovchilar ro'yxati.
"""
from aiogram import types
from aiogram.dispatcher import FSMContext
from html import escape

from bot_instance import bot, dp
from config import ADMINS, TARIFFS
from storage import get_user, save_users, users_store
from states import DriverStates
from utils import display_name
from stickers import send_sticker_safe
from keyboards import (
    driver_apply_kb, main_menu_kb, driver_main_kb,
    admin_driver_decision_kb, admin_driver_manage_kb, phone_request_kb,
    admin_add_driver_confirm_kb,
)


async def notify_admins_new_application(uid: str, full_name: str, username: str):
    kb = admin_driver_decision_kb(uid)
    username_display = f"@{username}" if username else "—"
    notifs = []
    for admin in ADMINS:
        try:
            msg = await bot.send_message(
                admin,
                f"🚘 <b>Yangi haydovchilik arizasi</b>\n\n"
                f"👤 Ism: <b>{escape(full_name)}</b>\n"
                f"🔗 Username: {username_display}\n"
                f"🆔 ID: <code>{uid}</code>\n"
                f"📞 Telefon: {get_user(uid).get('phone') or 'Hali kiritilmagan'}\n"
                f"📋 Batafsil ma’lumot va profil quyidagi tugmalarda.",
                reply_markup=kb,
            )
            notifs.append({"admin": admin, "msg_id": msg.message_id})
        except Exception:
            pass
    users_store.data["admin_notifs"][uid] = notifs
    await save_users()


async def render_driver_section(chat_id: int, uid: int, state: FSMContext):
    uid_s = str(uid)
    u = get_user(uid_s)

    if uid in ADMINS:
        if u["driver_status"] != "approved":
            u["driver_status"] = "approved"
            u["driver_paused"] = False
            u["subscription"]["active"] = True
            await save_users()
        return await bot.send_message(chat_id, "Haydovchi bo‘limi (admin):", reply_markup=driver_main_kb())

    status = u["driver_status"]
    if status in ("none", "rejected"):
        text = "Siz hali haydovchi emassiz. Ariza yuboring." if status == "none" \
            else "❌ Admin arizangizni rad etgan edi. Xohlasangiz qayta ariza yuborishingiz mumkin."
        return await bot.send_message(chat_id, text, reply_markup=driver_apply_kb())

    if status == "pending":
        return await bot.send_message(chat_id, "⏳ Arizangiz admin tomonidan ko‘rib chiqilmoqda…", reply_markup=main_menu_kb())

    # status == approved
    if not u.get("phone"):
        await state.set_state(DriverStates.waiting_phone)
        return await bot.send_message(
            chat_id,
            "📱 Iltimos, telefon raqamingizni yuboring.\n"
            "Tugma orqali yoki qo‘lda kiritishingiz mumkin (masalan: 901234567).",
            reply_markup=phone_request_kb(),
        )

    if not u["subscription"].get("active"):
        from handlers.payment import show_tariffs
        return await show_tariffs(chat_id)

    await bot.send_message(chat_id, "Haydovchi bo‘limi:", reply_markup=driver_main_kb())


@dp.callback_query_handler(lambda c: c.data == "menu:driver", state="*")
async def driver_section_cb(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    try:
        await call.message.edit_reply_markup()
    except Exception:
        pass
    await render_driver_section(call.message.chat.id, call.from_user.id, state)
    await call.answer()


@dp.callback_query_handler(lambda c: c.data == "drv_apply")
async def driver_apply(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    u = get_user(uid)

    if u["driver_status"] == "pending":
        return await call.answer("Siz allaqachon ariza yuborgansiz. Iltimos kuting.", show_alert=True)
    if u["driver_status"] == "approved":
        return await call.answer("Siz allaqachon tasdiqlangan haydovchisiz.", show_alert=True)

    if not u.get("phone"):
        state = dp.current_state(chat=call.from_user.id, user=call.from_user.id)
        await state.update_data(driver_application=True)
        await state.set_state(DriverStates.waiting_phone)
        await call.message.answer("Ariza uchun avval telefon raqamingizni yozing:", reply_markup=phone_request_kb())
        return await call.answer()

    u["full_name"] = call.from_user.full_name or u.get("full_name", "")
    u["username"] = call.from_user.username or u.get("username", "")
    await save_users()
    from handlers.payment import show_tariffs
    await call.message.answer(
        "✅ Ma’lumotlaringiz saqlandi. Endi tarifni tanlab, to‘lov arizasini yuboring.",
    )
    await show_tariffs(call.message.chat.id)
    await call.answer()


@dp.callback_query_handler(lambda c: c.data and c.data.split(":")[0] in
                            ("drv_ok", "drv_no", "drv_view", "drv_remove", "drv_keep"))
async def admin_driver_action(call: types.CallbackQuery):
    if call.from_user.id not in ADMINS:
        return await call.answer("Faqat adminlar uchun.", show_alert=True)

    action, _, uid = call.data.partition(":")
    if not uid:
        return await call.answer("Xatolik.", show_alert=True)

    u = get_user(uid)

    if action == "drv_ok":
        u["driver_status"] = "approved"
        u["driver_paused"] = True
        await save_users()
        await _update_admin_notifs(uid, "✅ Amal bajarildi (tasdiqlandi)")

        try:
            state = dp.current_state(chat=int(uid), user=int(uid))
            await state.set_state(DriverStates.waiting_phone)
            await bot.send_message(
                int(uid),
                "🎉 Admin sizni haydovchi sifatida tasdiqladi!\n\n"
                "📱 Endi telefon raqamingizni yuboring — tugma orqali yoki qo‘lda "
                "(masalan: 901234567).",
                reply_markup=phone_request_kb(),
            )
            await send_sticker_safe(int(uid), "driver_approved")
        except Exception:
            pass
        await call.answer("Tasdiqlandi ✅")

    elif action == "drv_no":
        from states import AdminStates
        state = dp.current_state(chat=call.from_user.id, user=call.from_user.id)
        await state.set_data({"reject_uid": uid})
        await state.set_state(AdminStates.rejection_reason)
        await bot.send_message(call.from_user.id, "Rad etish sababini yozing (bekor qilish uchun /start):")
        await call.answer()

    elif action == "drv_view":
        name = display_name(u, uid)
        sub = u.get("subscription", {})
        sub_text = "faol ✅" if sub.get("active") else "faol emas ❌"
        txt = (
            f"🚘 <b>Haydovchi ma'lumotlari</b>\n\n"
            f"👤 Ism: <b>{name}</b>\n"
            f"🆔 ID: <code>{uid}</code>\n"
            f"📞 Telefon: {u.get('phone') or '—'}\n"
            f"📋 Status: {u.get('driver_status', '—')}\n"
            f"💳 Obuna: {sub_text}\n"
            f"📦 Tarif: {sub.get('tariff') or '—'}\n"
            f"📅 Tugashi: {__import__('utils').fmt_date(sub['end']) if sub.get('end') else 'Muddatsiz / mavjud emas'}\n"
            f"🔗 Username: @{u.get('username') or '—'}"
        )
        await bot.send_message(call.from_user.id, txt, reply_markup=admin_driver_manage_kb(uid))
        await call.answer()

    elif action == "drv_remove":
        u["driver_status"] = "rejected"
        u["driver_paused"] = True
        u["subscription"]["active"] = False

        from storage import ads_store, save_ads
        ads_stopped = False
        for ad in ads_store.data["driver"].values():
            if ad.get("user") == uid and ad.get("active", False):
                ad["active"] = False
                ads_stopped = True
        if ads_stopped:
            await save_ads()

        await save_users()
        await call.answer("Foydalanuvchi chiqarib tashlandi, e’lonlari to‘xtatildi.")
        try:
            await bot.send_message(
                int(uid),
                "❌ Siz haydovchilar ro‘yxatidan chiqarib tashlandingiz. "
                "Faol e’loningiz ham to‘xtatildi va botdan haydovchi sifatida "
                "foydalana olmaysiz.",
                reply_markup=main_menu_kb(),
            )
        except Exception:
            pass

    elif action == "drv_keep":
        u["driver_status"] = "approved"
        await save_users()
        await call.answer("Foydalanuvchi haydovchi sifatida qoldirildi.")
        try:
            await bot.send_message(int(uid), "✅ Siz haydovchi sifatida qoldirildingiz.", reply_markup=driver_main_kb())
        except Exception:
            pass


async def _update_admin_notifs(uid: str, new_text: str):
    notifs = users_store.data.get("admin_notifs", {}).get(uid, [])
    for item in notifs:
        try:
            await bot.edit_message_text(new_text, item["admin"], item["msg_id"])
        except Exception:
            pass


@dp.callback_query_handler(lambda c: c.data == "menu:admin_drivers", state="*")
async def admin_drivers_list(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMINS:
        return await call.answer("Faqat adminlar uchun.", show_alert=True)
    await state.finish()

    kb = types.InlineKeyboardMarkup()
    found = False
    for uid, u in users_store.data["users"].items():
        if u.get("driver_status") == "approved":
            kb.add(types.InlineKeyboardButton(display_name(u, uid), callback_data=f"drv_view:{uid}"))
            found = True
    kb.add(types.InlineKeyboardButton("🏠 Bosh menyu", callback_data="menu:home"))

    if not found:
        try:
            await call.message.edit_text("Hozircha tasdiqlangan haydovchilar yo‘q.", reply_markup=kb)
        except Exception:
            await call.message.answer("Hozircha tasdiqlangan haydovchilar yo‘q.", reply_markup=kb)
        return await call.answer()

    try:
        await call.message.edit_text("📋 Tasdiqlangan haydovchilar ro‘yxati:", reply_markup=kb)
    except Exception:
        await call.message.answer("📋 Tasdiqlangan haydovchilar ro‘yxati:", reply_markup=kb)
    await call.answer()


from states import AdminStates
from html import escape

@dp.message_handler(state=AdminStates.rejection_reason, content_types=["text"])
async def reject_with_reason(message, state):
    if message.from_user.id not in ADMINS:
        return
    data = await state.get_data()
    if data.get("reject_payment"):
        from storage import payments_store, save_payments
        from handlers.payment_admin import _update_payment_notifs
        pid = data["reject_payment"]
        payment = payments_store.data["payments"].get(pid)
        if not payment or payment["status"] != "pending":
            await state.finish()
            return await message.answer("Bu to‘lov allaqachon ko‘rib chiqilgan.")
        payment["status"] = "rejected"
        payment["rejection_reason"] = message.text[:700]
        await save_payments()
        if payment.get("driver_application"):
            rejected_user = get_user(payment["uid"])
            rejected_user["driver_status"] = "rejected"
            rejected_user["driver_paused"] = True
            await save_users()
        await state.finish()
        text = "❌ To‘lov rad etildi. Sabab: " + escape(message.text[:700])
        await _update_payment_notifs(pid, text)
        try:
            await bot.send_message(int(payment["uid"]), text + "\n\nQayta ariza berish uchun haydovchi bo‘limiga kiring.", reply_markup=driver_apply_kb())
        except Exception:
            await message.answer("Foydalanuvchiga xabar yetkazilmadi.")
        return await message.answer("✅ Sabab saqlandi.", reply_markup=main_menu_kb(is_admin=True))
    uid = data["reject_uid"]
    u = get_user(uid)
    u["driver_status"] = "rejected"
    u["driver_paused"] = True
    u["rejection_reason"] = message.text[:700]
    await save_users()
    await state.finish()
    await _update_admin_notifs(uid, "❌ Rad etildi: " + escape(message.text[:700]))
    try:
        await bot.send_message(int(uid), "❌ Arizangiz rad etildi.\nSabab: " + escape(message.text[:700]), reply_markup=main_menu_kb())
    except Exception:
        await message.answer("Qaror saqlandi, lekin foydalanuvchiga xabar yetkazilmadi.")
    await message.answer("✅ Rad etish sababi saqlandi.", reply_markup=main_menu_kb(is_admin=True))


@dp.callback_query_handler(lambda c: c.data.startswith("admin_extend:"), state="*")
async def admin_extend_menu(call):
    if call.from_user.id not in ADMINS:
        return await call.answer("Faqat admin uchun.", show_alert=True)
    from config import TARIFFS
    uid = call.data.split(":")[1]
    kb = types.InlineKeyboardMarkup(row_width=2)
    for key, tariff in TARIFFS.items():
        kb.insert(types.InlineKeyboardButton(tariff["label"], callback_data=f"admin_grant:{uid}:{key}"))
    await call.message.answer("Qo‘shiladigan obuna muddatini tanlang:", reply_markup=kb)
    await call.answer()


@dp.callback_query_handler(lambda c: c.data.startswith("admin_grant:"), state="*")
async def admin_grant(call):
    if call.from_user.id not in ADMINS:
        return await call.answer("Faqat admin uchun.", show_alert=True)
    from config import TARIFFS
    from utils import extend_subscription, fmt_date
    _, uid, key = call.data.split(":")
    if key not in TARIFFS:
        return await call.answer("Tarif topilmadi.", show_alert=True)
    u = get_user(uid)
    if u["driver_status"] != "approved":
        return await call.answer("Avval haydovchini tasdiqlang.", show_alert=True)
    end = extend_subscription(u, TARIFFS[key])
    await save_users()
    await call.message.edit_reply_markup()
    text = "✅ Obuna uzaytirildi. Tugashi: " + (fmt_date(end) if end else "Umrbod")
    await call.message.answer(text)
    try:
        await bot.send_message(int(uid), text, reply_markup=driver_main_kb())
    except Exception:
        await call.message.answer("Haydovchiga xabar yetkazilmadi.")
    await call.answer()


@dp.callback_query_handler(lambda c: c.data == "menu:admin_add_driver", state="*")
async def admin_add_driver_start(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMINS:
        return await call.answer("Faqat admin uchun.", show_alert=True)
    await state.finish()
    await state.set_state(AdminStates.add_driver_id)
    await call.message.answer(
        "🧑‍✈️ Shofyor Telegram ID raqamini yuboring.\n\n"
        "Masalan: <code>123456789</code>",
    )
    await call.answer()


@dp.message_handler(state=AdminStates.add_driver_id, content_types=["text"])
async def admin_add_driver_id(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMINS:
        return
    uid = message.text.strip().removeprefix("+")
    if not uid.isdigit():
        return await message.answer("❌ ID faqat raqamlardan iborat bo‘lishi kerak. Qayta yuboring:")
    user = get_user(uid)
    await state.update_data(add_driver_uid=uid)
    kb = types.InlineKeyboardMarkup(row_width=2)
    for key, tariff in TARIFFS.items():
        kb.insert(types.InlineKeyboardButton(
            f"{tariff['label']} — {tariff['price']:,}".replace(",", " ") + " so‘m",
            callback_data=f"admin_add_tariff:{uid}:{key}",
        ))
    await message.answer(
        f"👤 ID: <code>{uid}</code>\n"
        f"📞 Telefon: {user.get('phone') or 'kiritilmagan'}\n\n"
        "Tarifni tanlang:",
        reply_markup=kb,
    )


@dp.callback_query_handler(lambda c: c.data.startswith("admin_add_tariff:"), state="*")
async def admin_add_driver_tariff(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMINS:
        return await call.answer("Faqat admin uchun.", show_alert=True)
    _, uid, tariff_key = call.data.split(":")
    tariff = TARIFFS.get(tariff_key)
    if not tariff:
        return await call.answer("Tarif topilmadi.", show_alert=True)
    await state.update_data(add_driver_uid=uid, add_driver_tariff=tariff_key)
    await call.message.edit_text(
        f"🧑‍✈️ Shofyor ID: <code>{uid}</code>\n"
        f"📦 Tarif: <b>{tariff['label']}</b>\n"
        f"💰 Narx: <b>{tariff['price']:,}</b> so‘m\n\n"
        "To‘lovsiz avtomatik tasdiqlaysizmi?",
        reply_markup=admin_add_driver_confirm_kb(uid, tariff_key),
    )
    await call.answer()


@dp.callback_query_handler(lambda c: c.data == "admin_add_cancel", state="*")
async def admin_add_driver_cancel(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMINS:
        return await call.answer("Faqat admin uchun.", show_alert=True)
    await state.finish()
    await call.message.edit_text("❌ Shofyor qo‘shish bekor qilindi.", reply_markup=main_menu_kb(is_admin=True))
    await call.answer()


@dp.callback_query_handler(lambda c: c.data.startswith("admin_add_confirm:"), state="*")
async def admin_add_driver_confirm(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMINS:
        return await call.answer("Faqat admin uchun.", show_alert=True)
    _, uid, tariff_key = call.data.split(":")
    tariff = TARIFFS.get(tariff_key)
    if not tariff:
        return await call.answer("Tarif topilmadi.", show_alert=True)
    user = get_user(uid)
    from utils import extend_subscription, fmt_date
    end = extend_subscription(user, tariff)
    user["driver_status"] = "approved"
    user["driver_paused"] = not bool(user.get("phone"))
    user.pop("rejection_reason", None)
    await save_users()
    await state.finish()
    expiry = "umrbod" if end is None else fmt_date(end)
    result = f"✅ Shofyor <code>{uid}</code> avtomatik tasdiqlandi.\n📦 Tarif: {tariff['label']}\n📅 Tugashi: {expiry}"
    await call.message.edit_text(result, reply_markup=main_menu_kb(is_admin=True))
    try:
        await bot.send_message(
            int(uid),
            f"🎉 Admin sizni shofyor sifatida avtomatik tasdiqladi!\n"
            f"📦 Tarif: <b>{tariff['label']}</b>\n📅 Tugashi: {expiry}",
            reply_markup=driver_main_kb() if user.get("phone") else main_menu_kb(),
        )
    except Exception:
        pass
    await call.answer("Tasdiqlandi ✅")
