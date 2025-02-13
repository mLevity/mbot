# config.py
BOT_TOKEN = "8179936211:AAHXPGFiaykjgVtXczDsUR-GnM0DpuSwmms"
ADMINS_ID = [859330334, 5816414679]
CHANNEL_ID = -1002252306584
admin_help = (
        "🔒 Admin commands:\n"
        "/view_user [telegram_id|username] - Чекнуть юзера\n"
        "/edit_user [telegram_id|username] [field] [value] - Поменять поле у пользователя\n"
        "/delete_user [telegram_id|username] - Delete user\n"
        "/message [telegram_id|username] [message] - Send message to user\n"
        "/message_all [message] - Рассылка\n"
        "/daily - Начислить проценты"
    )
rules_text = "RULES: https://telegra.ph/LUMINA-TRADE-RULES-02-12"
tariffs = {
        'base': 0.5,  # Базовый тариф (всегда действует)
        'plus': 1.0,  # Plus: 1% в день
        'max': 2.0,   # Max: 2% в день
        'ultra': 3.0  # Ultra: 3% в день
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
    'BTC':'bc1qx7ppkupeqyrrnm4z0djlpwcpml0qmplnaa875p',
    'ETH':'0x4FC9C39BDfA9Cf2B2992A30e2a35A57DDd08dBF9'
}
# Реферальный бонус (в долларах)
REFERRAL_BONUS = 1.0

# Ссылка на поддержку
SUPPORT_LINK = "https://t.me/luminatrade_support_bot"
