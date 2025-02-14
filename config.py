# config.py
BOT_TOKEN = "5676131920:AAH19J_Jcyv3qL-pIo7Tc4-SSiF4gWbsQxs"
ADMINS_ID = [859330334, 5816414679]
CHANNEL_ID = -1002252306584
admin_help = (
        "🔒 Admin commands:\n"
        "/view_user [telegram_id|username] - Чекнуть юзера\n"
        "/edit_user [telegram_id|username] [field] [value] - ПЕРЕД ИЗМЕНЕИЕМ ПОСМОТРИ ПОЛЯ ЮЗЕРА\n"
        "/view_all_users Чекнуть всех юзеров"
        "/delete_user [telegram_id|username] - Delete user\n"
        "/message [telegram_id|username] [message] - Send message to user\n"
        "/message_all [message] - Рассылка\n"
        "/daily - Начислить проценты"
        ""
    )
bonuses_text = (
    "🎥 *Make a TikTok or Reels about our bot and earn REAL CASH!* 💰\n\n"
    "- 10,000 views = $50 straight to your account or free MAX boost level access.\n"
    "- 100,000 views = $500 bonus + 1 month MAX boost level access\n"
    "- 1 MILLION views = $5,000 bonus + lifetime MAX boost level access. 🚀\n\n"
    "🔥 *It’s simple:*\n"
    "  1 - Create a video about our bot (we’ll help with ideas).\n"
    "  2 - Post it with #LUMINATRADE.\n"
    "  3 - Send us the link — and get paid as soon as you hit the views.\n\n"
    "💡 *This offer won’t last forever. Act now before it’s gone!*\n"
)
rules_text = "RULES: https://telegra.ph/LUMINA-TRADE-RULES-02-12"
tariffs = {
        'base': 1.0,  # Базовый тариф (всегда действует)
        'plus': 2.0,  # Plus: 1% в день
        'max': 5.0,   # Max: 2% в день
        'ultra': 10.0  # Ultra: 3% в день
    }
rates = {'BTC': 100000, 'ETH': 3000}
# Минимальная сумма для вывода
MIN_WITHDRAWAL_AMOUNT = {
    'USDT': 100,
    'BTC': 0.001,
    'ETH': 0.04
}
wallets = {
    'USDT':'TB1sNAAvRC5uNHHw4qta8nkn16WzgXE7KN',
    'USDT[TRC20]':'TB1sNAAvRC5uNHHw4qta8nkn16WzgXE7KN',
    'BTC':'bc1qx7ppkupeqyrrnm4z0djlpwcpml0qmplnaa875p',
    'ETH':'0x4FC9C39BDfA9Cf2B2992A30e2a35A57DDd08dBF9'
}
# Реферальный бонус (в долларах)
REFERRAL_BONUS = 1.0

# Ссылка на поддержку
SUPPORT_LINK = "@luminatrade_support_bot"