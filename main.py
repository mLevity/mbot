from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, constants
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)
import sqlite3
import time
import config  


conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()


cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    telegram_id TEXT UNIQUE,
    username TEXT UNIQUE,
    balance REAL DEFAULT 0,
    referrer_id TEXT,
    referrals_count INTEGER DEFAULT 0,
    referral_earnings REAL DEFAULT 0,
    total_deposits REAL DEFAULT 0,
    tariff TEXT DEFAULT 'base',
    days_left INTEGER DEFAULT 0,
    earnings REAL DEFAULT 0,
    total_withdraws REAL DEFAULT 0
)''')


def check_username(update: Update):
    if not update.effective_user.username:
        update.message.reply_text(
            "🤖 The bot requires you to have a username set in Telegram. Please set a username in your Telegram settings and try again."
        )
        return False
    return True


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_username(update):
        return
    user_id = update.effective_user.id
    username = update.effective_user.username
    cursor.execute("SELECT * FROM users WHERE telegram_id=?", (user_id,))
    if not cursor.fetchone():
        referrer_id = context.args[0] if context.args else None
        cursor.execute(
            "INSERT INTO users (telegram_id, username, balance, referrer_id) VALUES (?, ?, ?, ?)",
            (user_id, username, 0, referrer_id)
        )
        conn.commit()
        if referrer_id:
            cursor.execute("UPDATE users SET referrals_count=referrals_count+1, balance=balance+? WHERE telegram_id=?", (config.REFERRAL_BONUS, referrer_id))
            conn.commit()
            cursor.execute("UPDATE users SET balance = 10.0 WHERE telegram_id = ?", user_id)
            conn.commit()
            await send_message(
                chat_id = referrer_id,
                text = f"🎉You have a new referral user!\n✅You received a $1 bonus"
            )
            await update.message.reply_text(f"🎉 You registered via a referral link! Your referrer received a ${config.REFERRAL_BONUS} bonus.\n✅You received a $10 welcome-bonus")

    chat_member = await context.bot.get_chat_member(chat_id=config.CHANNEL_ID, user_id=user_id)
    if chat_member.status not in ['member', 'administrator', 'creator']:
            await update.message.reply_text("Please subscribe our channel to continue: @luminatrade")
            return
    message = await update.message.reply_text(
        "*✨ Welcome to CryptoBoost!*\n\nBy using this bot, you agree to the rules.\n\nChoose an option from the menu below.",
        reply_markup=get_main_menu(),
        parse_mode=constants.ParseMode.MARKDOWN
    )
    context.user_data['last_message_id'] = message.message_id


def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("✅Withdraw", callback_data='withdraw_funds'),InlineKeyboardButton("🔄 Invest", callback_data='popup_balance')],
        [InlineKeyboardButton("🎁 Change Boost Level", callback_data='buy_tariff')],
        [InlineKeyboardButton("👥 Referral System", callback_data='referral_system')],
        [InlineKeyboardButton("📊 Statistics", callback_data='statistics')],
        [InlineKeyboardButton("❓ Help", callback_data='help'), InlineKeyboardButton("📖 Rules", callback_data='rules')]
    ]
    return InlineKeyboardMarkup(keyboard)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not check_username(update):
        return

    last_message_id = context.user_data.get('last_message_id')
    chat_id = query.message.chat_id


    if query.data == 'popup_balance':
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=last_message_id,
            text="*💸 Select a payment method:*",
            reply_markup=get_payments_menu(),
            parse_mode=constants.ParseMode.MARKDOWN
        )

    elif query.data.startswith('choose_currency_'):
        currency = query.data.split('_')[-1].upper()
        context.user_data['currency'] = currency
        context.user_data['is_deposit'] = True
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=last_message_id,
            text=f"⚡*You selected* {currency}.\nEnter the deposit amount:",
            parse_mode=constants.ParseMode.MARKDOWN
        )

    elif query.data == 'confirm_payment':
        currency = context.user_data.get('currency')
        amount = context.user_data.get('amount')
        print(currency)
        wallet_address = config.wallets[currency]

        if not all([currency, amount, wallet_address]):
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=last_message_id,
                text="*⚠️ An error occurred. Please try again.*",
                reply_markup=get_main_menu(),
                parse_mode=constants.ParseMode.MARKDOWN
            )
            return

        reply_text = f"Send `{amount}` {currency} to the following address:\n\n`{wallet_address}`\n\nAfter sending, click the 'Check Payment' button."
        keyboard = [[InlineKeyboardButton("✅ Check Payment", callback_data='check_payment')]]
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=last_message_id,
            text=reply_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=constants.ParseMode.MARKDOWN
        )

    elif query.data == 'check_payment':
        currency = context.user_data.get('currency')
        amount = context.user_data.get('amount')
        wallet_address = config.wallets[currency]

        if not all([currency, amount, wallet_address]):
            await context.bot.send_message(
                chat_id=chat_id,
                text="*⚠️ An error occurred. Please try again.*",
                reply_markup=get_main_menu(),
                parse_mode=constants.ParseMode.MARKDOWN
            )
            return

        await context.bot.send_message(
            chat_id=chat_id,
            text=f"*❌ Payment of {amount} {currency} not found. Please try again later or contact support*",
            parse_mode=constants.ParseMode.MARKDOWN
        )
    elif query.data == 'withdraw_funds':
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=last_message_id,
            text="*💸 Select withdrawal currency:*",
            reply_markup=get_withdrawal_menu(),
            parse_mode=constants.ParseMode.MARKDOWN
        )

    elif query.data.startswith('withdraw_currency_'):
        currency = query.data.split('_')[-1].upper()
        min_amount = config.MIN_WITHDRAWAL_AMOUNT[currency]
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=last_message_id,
            text=f"⚡ *You selected* {currency}.\nEnter the withdrawal amount (min: {min_amount}):",
            parse_mode=constants.ParseMode.MARKDOWN
        )
        context.user_data['withdraw_currency'] = currency
        context.user_data['is_withdrawal'] = True

    elif query.data == 'buy_tariff':
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=last_message_id,
            text="*🎁 Select a boost level:*",
            reply_markup=get_tariff_menu(),
            parse_mode=constants.ParseMode.MARKDOWN
        )

    elif query.data == 'referral_system':
        referral_link = f"https://t.me/{context.bot.username}?start={query.from_user.id}"
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=last_message_id,
            text=f"*👥 Your referral link:*\n`{referral_link}`\n\n\n *Get 1$ for every user entered with your link!\nMore bonuses for tiktok and reels (contact support)*",
            reply_markup=get_main_menu(),
            parse_mode=constants.ParseMode.MARKDOWN
        )

    elif query.data == 'statistics':
        user_id = query.from_user.id
        cursor.execute("SELECT balance,tariff, days_left, referrals_count, referral_earnings, total_deposits,  earnings, total_withdraws FROM users WHERE telegram_id=?", (user_id,))
        balance,tariff, days_left, referrals_count, referral_earnings, total_deposits, earnings, total_withdraws = cursor.fetchone()
        
        percent = config.tariffs[tariff]
        if days_left == 0:
            days_left = '∞'
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=last_message_id,
            text = f"💲 *Balance:* ${balance}\n" \
                f"🚀 *Boost Level:* {tariff}\n" \
                f"⭐ *Growth:* {percent}%\n" \
                f"⏳ *Days left:* {days_left}\n" \
                f"👥 *Referrals:* {referrals_count}\n" \
                f"💵 *Referral Earnings:* ${referral_earnings}\n" \
                f"📊 *Total Deposits:* ${total_deposits}\n" \
                f"📈 *Earnings:* ${earnings}\n" \
                f"💰 *Total withdrawals:* ${total_withdraws}",
            parse_mode=constants.ParseMode.MARKDOWN
        )

    elif query.data == 'help':
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=last_message_id,
            text=f"Need help? Contact support: {config.SUPPORT_LINK}",
            reply_markup=get_main_menu()
        )

    elif query.data == 'rules':
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=last_message_id,
            text=config.rules_text,
            reply_markup=get_main_menu(),
            parse_mode=constants.ParseMode.MARKDOWN
        )
 
    elif query.data in ['buy_plus', 'buy_max', 'buy_ultra']:
        user_id = query.from_user.id
        cursor.execute("SELECT balance FROM users WHERE telegram_id=?", (user_id,))
        balance = cursor.fetchone()[0]
        prices = {
            'plus': 50,  # Plus: $50
            'max': 100,  # Max: $100
            'ultra': 200  # Ultra: $200
        }
        days = {
            'plus': 20,  # Plus: 20
            'max': 10,   # Max: 10 
            'ultra': 5   # Ultra: 5
        }
        tariff_name = query.data.split('_')[1]
        price = prices[tariff_name]
        if balance >= price:
            message = f"You successfully bought *{tariff_name}* boost level!"
            cursor.execute("UPDATE users SET balance=balance-?, tariff=?, days_left=? WHERE telegram_id=?",
                           (price, tariff_name, days[tariff_name], user_id))
            conn.commit()
            await query.message.reply_text(message)
        else:
            await query.message.reply_text("⚠️*Insufficient funds on your balance!*")
        await query.message.reply_text("Main menu:", reply_markup=get_main_menu())

    elif query.data == 'back_to_main':
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=last_message_id,
            text="*🏠 Main Menu:*",
            reply_markup=get_main_menu(),
            parse_mode=constants.ParseMode.MARKDOWN
        )


def get_payments_menu():
    keyboard = [
        [InlineKeyboardButton("USDT[TRC20]", callback_data='choose_currency_usdt')],
        [InlineKeyboardButton("BTC", callback_data='choose_currency_btc')],
        [InlineKeyboardButton("ETH", callback_data='choose_currency_eth')],
        [InlineKeyboardButton("🔙 Back", callback_data='back_to_main')]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_withdrawal_menu():
    keyboard = [
        [InlineKeyboardButton("USDT", callback_data='withdraw_currency_usdt')],
        [InlineKeyboardButton("BTC", callback_data='withdraw_currency_btc')],
        [InlineKeyboardButton("ETH", callback_data='withdraw_currency_eth')],
        [InlineKeyboardButton("🔙 Back", callback_data='back_to_main')]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_tariff_menu():
    keyboard = [
        [InlineKeyboardButton("Plus ($50)", callback_data='buy_plus')],
        [InlineKeyboardButton("Max ($100)", callback_data='buy_max')],
        [InlineKeyboardButton("Ultra ($200)", callback_data='buy_ultra')],
        [InlineKeyboardButton("🔙 Back", callback_data='back_to_main')]
    ]
    return InlineKeyboardMarkup(keyboard)


async def handle_deposit_withdraw_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('is_withdrawal'):
        try:
            amount = float(update.message.text)
            currency = context.user_data.get('withdraw_currency')
            min_amount = config.MIN_WITHDRAWAL_AMOUNT.get(currency, 0)

            if amount < min_amount:
                await context.bot.send_message(
                    chat_id=update.message.chat_id,
                    text=f"*⚠️ Minimum withdrawal amount for {currency} is {min_amount}.*",
                    parse_mode=constants.ParseMode.MARKDOWN
                )
                return
            user_id = update.effective_user.id
            cursor.execute("SELECT balance FROM users WHERE telegram_id=?", (user_id,))
            balance = cursor.fetchone()[0]
            if currency in ['BTC', 'ETH']:
                balance = balance/config.rates[currency]
                amount = amount*config.rates[currency]
            if amount > balance:
                await context.bot.send_message(
                    chat_id=update.message.chat_id,
                    text="⚠️*Insufficient funds on your balance!*",
                    parse_mode=constants.ParseMode.MARKDOWN
                )
                return

            cursor.execute("UPDATE users SET balance=balance-?, total_withdraws=total_withdraws+? WHERE telegram_id=?", (amount, amount, user_id))
            conn.commit()

            await context.bot.send_message(
                chat_id=update.message.chat_id,
                text=f"*✅ Withdrawal of {amount} {currency} successful!*\nYour balance has been updated.\nContact support to continue",
                parse_mode=constants.ParseMode.MARKDOWN
            )

            context.user_data.pop('is_withdrawal', None)

        except ValueError:
            await context.bot.send_message(
                chat_id=update.message.chat_id,
                text="*⚠️ Invalid amount. Please enter a positive number.*",
                parse_mode=constants.ParseMode.MARKDOWN
            )

    elif context.user_data.get('is_deposit'):
        try:
            amount = float(update.message.text)

            if amount <= 0:
                raise ValueError

            currency = context.user_data.get('currency')
            if not currency:
                await context.bot.send_message(
                    chat_id=update.message.chat_id,
                    text="*⚠️ An error occurred. Please try again.*",
                    parse_mode=constants.ParseMode.MARKDOWN
                )
                return

            wallet_address = config.wallets[currency]
            context.user_data['amount'] = amount
            context.user_data['wallet_address'] = wallet_address

            reply_text = f"You want to deposit `{amount}` {currency}. Confirm the action."
            keyboard = [[InlineKeyboardButton("✅ Confirm", callback_data='confirm_payment')]]

            last_message_id = context.user_data.get('last_message_id')
            if last_message_id:
                await context.bot.edit_message_text(
                    chat_id=update.message.chat_id,
                    message_id=last_message_id,
                    text=reply_text,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode=constants.ParseMode.MARKDOWN
                )
            else:
                await context.bot.send_message(
                    chat_id=update.message.chat_id,
                    text=reply_text,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode=constants.ParseMode.MARKDOWN
                )
            context.user_data.pop('is_deposit', None)
        except ValueError:
            await context.bot.send_message(
                chat_id=update.message.chat_id,
                text="*⚠️ Invalid amount. Please enter a positive number.*",
                parse_mode=constants.ParseMode.MARKDOWN
            )

    else:
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="*⚠️ An error occurred. Please try again.*",
            parse_mode=constants.ParseMode.MARKDOWN
        )

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in config.ADMINS_ID:
        await update.message.reply_text("❌ Access denied.")
        return
    await update.message.reply_text(config.admin_help)
async def daily_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in config.ADMINS_ID:
        await update.message.reply_text("❌ Access denied.")
        return
    try:
        # Первый запрос: обновление balance, days_left и earnings
        for tariff, rate in config['tariffs'].items():
            query_update = """
            UPDATE users
            SET 
                balance = balance + balance * ? / 100,
                days_left = days_left - 1,
                earnings = earnings + balance * ? / 100
            WHERE tariff = ?
            """
            cursor.execute(query_update, (rate, rate, tariff))

        # Второй запрос: сброс tariff до 'base', если days_left стало 0
        query_reset_tariff = """
        UPDATE users
        SET tariff = 'base'
        WHERE days_left = 0
        """
        cursor.execute(query_reset_tariff)

        # Фиксация изменений
        conn.commit()
    except Exception as e:
        # Отправка сообщения об ошибке
        update.message.reply_text(f"❌ An error occurred: {str(e)}")
        conn.rollback()

async def view_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in config.ADMINS_ID:
        await update.message.reply_text("❌ Access denied.")
        return
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /view_user [telegram_id|username]")
        return

    identifier = context.args[0]
    if identifier.isdigit():
        cursor.execute("SELECT * FROM users WHERE telegram_id=?", (identifier,))
    else:
        cursor.execute("SELECT * FROM users WHERE username=?", (identifier,))

    user = cursor.fetchone()
    if not user:
        await update.message.reply_text("User not found.")
        return

    user_id, telegram_id, username, balance, referrer_id, referrals_count, referral_earnings, total_deposits, tariff, days_left, earnings, total_withdraws = user
    await update.message.reply_text(
        f"*User Details:*\n"
        f"ID: `{user_id}`\n"
        f"Telegram ID: `{telegram_id}`\n"
        f"Username: `{username}`\n"
        f"Balance: ${balance}\n"
        f"Referrer ID: `{referrer_id}`\n"
        f"Referrals: {referrals_count}\n"
        f"Referral Earnings: ${referral_earnings}\n"
        f"Total Deposits: ${total_deposits}\n"
        f"Boost Level: {tariff}\n"
        f"Days Left: {days_left}\n"
        f"Earnings: ${earnings}\n"
        f"Total withdrawals: ${total_withdraws}",
        parse_mode=constants.ParseMode.MARKDOWN
    )

async def edit_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in config.ADMINS_ID:
        await update.message.reply_text("❌ Access denied.")
        return
    if len(context.args) != 3:
        cursor.execute('PRAGMA table_info("users")')
        coll_names = ' '.join([i[1]+' ' for i in cursor.fetchall()])
        await update.message.reply_text(f"Usage: /edit_user [telegram_id|username] [field] [value]\n\n{coll_names}")
        return

    identifier, field, value = context.args
    if identifier.isdigit():
        cursor.execute("SELECT * FROM users WHERE telegram_id=?", (identifier,))
    else:
        cursor.execute("SELECT * FROM users WHERE username=?", (identifier,))

    user = cursor.fetchone()
    if not user:
        await update.message.reply_text("User not found.")
        return

    try:
        cursor.execute(f"UPDATE users SET {field}=? WHERE telegram_id=?", (value, user[1]))
        conn.commit()
        await update.message.reply_text(f"Field `{field}` updated successfully.", parse_mode=constants.ParseMode.MARKDOWN)
    except Exception as e:
        await update.message.reply_text(f"Error updating field: {e}")

async def delete_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in config.ADMINS_ID:
        await update.message.reply_text("❌ Access denied.")
        return
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /delete_user [telegram_id|username]")
        return

    identifier = context.args[0]
    if identifier.isdigit():
        cursor.execute("DELETE FROM users WHERE telegram_id=?", (identifier,))
    else:
        cursor.execute("DELETE FROM users WHERE username=?", (identifier,))

    conn.commit()
    await update.message.reply_text("User deleted successfully.")

async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in config.ADMINS_ID:
        await update.message.reply_text("❌ Access denied.")
        return
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /message [telegram_id|username] [message]")
        return

    identifier = context.args[0]
    message = " ".join(context.args[1:])
    if identifier.isdigit():
        cursor.execute("SELECT telegram_id FROM users WHERE telegram_id=?", (identifier,))
    else:
        cursor.execute("SELECT telegram_id FROM users WHERE username=?", (identifier,))

    user = cursor.fetchone()
    if not user:
        await update.message.reply_text("User not found.")
        return

    try:
        await context.bot.send_message(chat_id=user[0], text=message)
        await update.message.reply_text("Message sent successfully.")
    except Exception as e:
        await update.message.reply_text(f"Failed to send message: {e}")

async def send_message_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in config.ADMINS_ID:
        await update.message.reply_text("❌ Access denied.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /message_all [message]")
        return

    message = " ".join(context.args)
    cursor.execute("SELECT telegram_id FROM users")
    users = cursor.fetchall()

    for user in users:
        try:
            await context.bot.send_message(chat_id=user[0], text=message)
        except Exception:
            continue

    await update.message.reply_text("Messages sent to all users.")
def main():
    application = Application.builder().token(config.BOT_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('admin_lvt', admin_panel))
    application.add_handler(CommandHandler('view_user', view_user))
    application.add_handler(CommandHandler('edit_user', edit_user))
    application.add_handler(CommandHandler('delete_user', delete_user))
    application.add_handler(CommandHandler('message', send_message))
    application.add_handler(CommandHandler('message_all', send_message_all))
    application.add_handler(CommandHandler('daily', daily_query))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_deposit_withdraw_amount))
    

    application.run_polling()

if __name__ == '__main__':
    main()
#5676131920:AAH19J_Jcyv3qL-pIo7Tc4-SSiF4gWbsQxs
