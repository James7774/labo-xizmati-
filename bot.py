"""
Labo Yuk Tashish Bot — Namangan va Farg'ona vodiysi uchun yuk tashish xizmati.
"""

import logging
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# ─── Logging ────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ─── Bot Token ──────────────────────────────────────────────────────────────
BOT_TOKEN = "8241236986:AAF9VVKzVFB1DgZBmdKqvzaj3ldUdzFzhrw"

# ─── Admins (Adminga yangi buyurtmalar haqida xabar boradi) ──────────────────
ADMINS = [8610001984]

# ─── Driver phone numbers ──────────────────────────────────────────────────
DRIVER_PHONES = ["+998950703345", "+998912933345"]

# ─── Conversation states ────────────────────────────────────────────────────
PHONE, CARGO_TYPE = range(2)

# ─── Main menu keyboard ─────────────────────────────────────────────────────
MAIN_MENU_KB = ReplyKeyboardMarkup(
    [
        ["🚗 Shafyor bilan bog'lanish"],
        ["📦 Buyurtma berish"],
    ],
    resize_keyboard=True,
)


# ═══════════════════════════════════════════════════════════════════════════
# /start
# ═══════════════════════════════════════════════════════════════════════════
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Greet user and show main menu."""
    await update.message.reply_text(
        "🚛 *Labo Yuk Tashish Bot*ga xush kelibsiz!\n\n"
        "Namangan va Farg'ona vodiysi bo'ylab yuk tashish xizmati.\n\n"
        "Quyidagi tugmalardan birini tanlang 👇",
        parse_mode="Markdown",
        reply_markup=MAIN_MENU_KB,
    )
    return ConversationHandler.END


# ═══════════════════════════════════════════════════════════════════════════
# 🚗 Shafyor bilan bog'lanish
# ═══════════════════════════════════════════════════════════════════════════
async def driver_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show clickable driver phone numbers."""
    # List of numbers clearly with Markdown links (these work for dialing)
    contact_text = (
        "🚗 *Shafyor bilan bog'lanish*\n\n"
        "Qo'ng'iroq qilish uchun quyidagi raqamlarni ustiga bosing:\n\n"
    )
    for phone in DRIVER_PHONES:
        contact_text += f"📞 [{phone}](tel:{phone})\n"

    # Inline buttons for navigation only
    inline_kb = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_menu")]]
    )

    await update.message.reply_text(
        contact_text,
        parse_mode="Markdown",
        reply_markup=inline_kb,
    )


# ═══════════════════════════════════════════════════════════════════════════
# 📦 Buyurtma berish  →  ask for phone
# ═══════════════════════════════════════════════════════════════════════════
async def order_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the order flow — ask for phone number."""
    phone_kb = ReplyKeyboardMarkup(
        [
            [KeyboardButton("📲 Telefon raqamni yuborish", request_contact=True)],
            ["⌨️ Raqamni yozish"],
            ["❌ Bekor qilish"],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await update.message.reply_text(
        "📦 *Buyurtma berish*\n\n"
        "Iltimos, telefon raqamingizni yuboring yoki yozib qoldiring 👇",
        parse_mode="Markdown",
        reply_markup=phone_kb,
    )
    return PHONE


# ═══════════════════════════════════════════════════════════════════════════
# Receive phone (contact or text) → ask cargo type
# ═══════════════════════════════════════════════════════════════════════════
async def receive_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Save phone and ask what cargo the user wants to ship."""
    if update.message.contact:
        contact = update.message.contact
        context.user_data["phone"] = contact.phone_number
        context.user_data["name"] = (
            f"{contact.first_name or ''} {contact.last_name or ''}".strip()
        )
    else:
        text = update.message.text
        if text == "⌨️ Raqamni yozish":
            await update.message.reply_text(
                "Iltimos, telefon raqamingizni kiriting:\n(Masalan: +998901234567)"
            )
            return PHONE
        
        # Simple validation could be added here
        context.user_data["phone"] = text
        context.user_data["name"] = update.message.from_user.first_name or "Mijoz"

    await update.message.reply_text(
        "✅ Telefon raqamingiz qabul qilindi!\n\n"
        "📦 *Yukingiz haqida batafsilroq ma'lumot bering*\n"
        "(Masalan: mebel, qurilish mollari, ko'ch-ko'ron va h.k.)",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(
            [["❌ Bekor qilish"]],
            resize_keyboard=True,
        ),
    )
    return CARGO_TYPE


# ═══════════════════════════════════════════════════════════════════════════
# Receive cargo type → confirm order
# ═══════════════════════════════════════════════════════════════════════════
async def receive_cargo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Save cargo type and confirm the order."""
    cargo = update.message.text
    context.user_data["cargo"] = cargo

    phone = context.user_data.get("phone", "—")
    name = context.user_data.get("name", "—")

    await update.message.reply_text(
        "✅ *Rahmat! Buyurtmangiz qabul qilindi.*\n\n"
        f"👤 Ism: {name}\n"
        f"📞 Telefon: {phone}\n"
        f"📦 Yuk turi: {cargo}\n\n"
        "Tez orada siz bilan bog'lanamiz! 🚛",
        parse_mode="Markdown",
        reply_markup=MAIN_MENU_KB,
    )

    # 🚨 Adminga xabar yuborish
    admin_msg = (
        "🆕 *Yangi buyurtma keldi!*\n\n"
        f"👤 *Mijoz:* {name}\n"
        f"📞 *Telefon:* {phone}\n"
        f"📦 *Yuk turi:* {cargo}"
    )
    for admin_id in ADMINS:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=admin_msg,
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Adminga (ID: {admin_id}) xabar yuborishda xatolik: {e}")

    # Clear user data for next order
    context.user_data.clear()
    return ConversationHandler.END


# ═══════════════════════════════════════════════════════════════════════════
# ❌ Bekor qilish (Cancel)
# ═══════════════════════════════════════════════════════════════════════════
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel order and return to main menu."""
    context.user_data.clear()
    await update.message.reply_text(
        "❌ Buyurtma bekor qilindi.\n\n"
        "Bosh menyu 👇",
        reply_markup=MAIN_MENU_KB,
    )
    return ConversationHandler.END


# ═══════════════════════════════════════════════════════════════════════════
# Inline callback: back to menu
# ═══════════════════════════════════════════════════════════════════════════
async def back_to_menu_cb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline 'back' button."""
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(
        "Bosh menyu 👇",
        reply_markup=MAIN_MENU_KB,
    )


# ═══════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════
def main() -> None:
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Conversation handler for ordering flow
    order_conv = ConversationHandler(
        entry_points=[
            MessageHandler(
                filters.Regex(r"^📦 Buyurtma berish$"), order_start
            ),
        ],
        states={
            PHONE: [
                MessageHandler(filters.CONTACT, receive_phone),
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND & ~filters.Regex(r"^❌ Bekor qilish$"),
                    receive_phone,
                ),
                MessageHandler(filters.Regex(r"^❌ Bekor qilish$"), cancel),
            ],
            CARGO_TYPE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND & ~filters.Regex(r"^❌ Bekor qilish$"),
                    receive_cargo,
                ),
                MessageHandler(filters.Regex(r"^❌ Bekor qilish$"), cancel),
            ],
        },
        fallbacks=[
            CommandHandler("start", start),
            MessageHandler(filters.Regex(r"^❌ Bekor qilish$"), cancel),
        ],
    )

    app.add_handler(order_conv)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(
            filters.Regex(r"^🚗 Shafyor bilan bog'lanish$"), driver_contact
        )
    )
    app.add_handler(CallbackQueryHandler(back_to_menu_cb, pattern="^back_to_menu$"))

    logger.info("🚛 Labo Yuk Tashish Bot ishga tushdi!")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
