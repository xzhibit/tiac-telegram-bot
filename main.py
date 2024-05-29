import logging

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# FAQ Data (Replace with your own content)
FAQ_DATA_EN = {
    "I have a claim under the contract. Can I file the Request for Arbitration with TIAC against the counterparty?": f"In order to confirm whether you can file the Request for Arbitration with TIAC, please check the dispute resolution provisions in your contract. Does it say that \"any dispute under this contract can be referred to arbitration under the Rules of the Tashkent International Arbitration Centre (TIAC) at the Chamber of Commerce and Industry of Uzbekistan\"?  If you are unsure, please send it to info@tiac.uz.",
    "How to file the Request for Arbitration?": "You can file the RfA here - https://tiac.webnyaya.com/RFA.",
    "I have other inquiries. How to contact TIAC?": "We answer all inquiries by email. Kindly send all your inquiries by email to info@tiac.uz and dbayzakova@tiac.uz. You will receive the response promptly.",
    "What is the tentative cost of arbitration under TIAC?": "There is a filing fee of USD 400, and the tentative arbitration costs can be calculated here: https://tiac.webnyaya.com/calculator .",
    "What are the TIAC bank account details?": "Account name: Tashkent International Arbitration Centre\n\nBank account for payment payments in Uzbek som (for Uzbek residents): 20212000505054469001\n\nBank account for USD payments (for non-residents inUzbekistan): 20212840105054469001\n\nBank account for Euro payments (for non-residents in Uzbekistan): 20212978905054469001\n\nName of the bank: OPERU AKB “KAPITALBANK”\n\nBank code: 00974\n\nTax identification number (TIN): 207290595\n\nSWIFT: KACHUZ22",
    # ... more FAQs
}

FAQ_DATA_RU = {  # First page of Russian FAQ
    "У меня есть иск/требование к контрагенту по договору. Могу ли я обратиться в TIAC?": "Чтобы подтвердить, можете ли вы подать Заявку на арбитраж в TIAC, ознакомьтесь с положениями о разрешении споров в Вашем контракте. Говорится ли там, что «любые споры подлежат окончательному урегулированию в соответствии с Арбитражным регламентом Ташкентского международного арбитражного центра (TIAC) при Торгово-промышленной палате Республики Узбекистан»? Если вы не уверены, отправьте копию контракта на адрес info@tiac.uz.",
    "Как подать Заявку на арбитраж в TIAC?": "Вы можете подать Заявку на арбитраж здесь — https://tiac.webnyaya.com/RFA.",
    "У меня есть другие вопросы. Как связаться с “TIAC”?": "Мы отвечаем на все запросы по электронной почте. Пожалуйста, направляйте все ваши запросы по электронной почте на адреса info@tiac.uz и dbayzakova@tiac.uz. Вы получите ответ оперативно.",
    "Каковы ориентировочные арбитражные расходы в TIAC?": "При подаче Заявки на арбитраж взимается регистрационный сбор в размере 400 долларов США, а ориентировочные арбитражные издержки можно рассчитать здесь: https://tiac.webnyaya.com/calculator.",
    "Каковы реквизиты банковского счета TIAC?": "Название счета: Ташкентский международный арбитражный центр\n\nБанковский счет для оплаты платежей в узбекских сумах (для резидентов Узбекистана): 20212000505054469001\n\nБанковский счет для платежей в долларах США (для нерезидентов вУзбекистан): 20212840105054469001\n\nБанковский счет для платежей в евро (для нерезидентов Узбекистана): 20212978905054469001\n\nНазвание банка: ОПЕРУ АКБ «КАПИТАЛБАНК»\n\nКод банка: 00974\n\nИНН: 207290595\n\nSWIFT: KACHUZ22"
}

FAQ_DATA_UZ = {
    "Shartnoma bo'yicha kontragentimga nisbatan da'vo/qarzim bor. TIACga murojaat qilsam bo'ladimi?": "TIACga arbitraj uchun da’vo arizani yuborishingiz mumkinligini tasdiqlash uchun shartnomangizdagi nizolarni hal qilish qoidalarini koʻrib chiqing. “Har qanday nizolar O‘zbekiston Respublikasi Savdo-sanoat palatasi huzuridagi Toshkent xalqaro arbitraj markazi (TIAC)ning arbitraj qoidalariga muvofiq yakuniy hal etilishi kerak” deb aytib o’tilganmi? Agar ishonchingiz komil bo'lmasa, shartnoma nusxasini info@tiac.uz  elektron manziliga yuboring.",
    "TIACga arbitraj uchun so'rovni qanday topshirishim mumkin?": "Arbitraj uchun so'rovni shu havola orqali yuborishingiz mumkin: https://tiac.webnyaya.com/RFA.",
    "Mening qo’shimcha savollarim bor. TIAC xodimlari bilan qanday bog'lanishim mumkin?": "Biz barcha so'rovlarga elektron pochta orqali javob beramiz. Qo’shimcha savollaringizni info@tiac.uz  va dbayzakova@tiac.uz  elektron pochta manzillariga yuboring. Siz darhol savollaringizga javob olasiz!",
    "TIACda arbitraj xarajatlari taxminan qancha?": "Arbitrajga da’vo ariza berishda 400 AQSh dollari miqdorida ro’yxatdan o’tish uchun to'lov olinadi,  taxminiy hakamlik xarajatlarini esa bu yerda hisoblash mumkin: https://tiac.webnyaya.com/calculator.",
    "TIACning bank hisobi rekvizitlari qanday?": "Hisob raqam nomlanishi:  Toshkent xalqaro arbitraj markazi\n\nO‘zbek so‘mida to‘lovlarni amalga oshirish uchun bank hisob raqami (O‘zbekiston rezidentlari uchun): 20212000505054469001\n\nAQSH dollarida to‘lovlarni amalga oshirish uchun bank hisob raqami (O‘zbekiston  norezidentlar uchun): 20212840105054469001\n\nYevroda to‘lovlarni amalga oshirish uchun bank hisob raqami (O‘zbekiston norezidentlari uchun): 20212978905054469001\n\nBank nomi: OPERU ATB \"KAPITALBANK\"\n\nBank kodi: 00974\n\nINN: 207290595\n\nSWIFT: KACHUZ22",
    # ... more FAQs in Uzbek
}

# Combine dictionaries for easy access
FAQ_DATA = {
    "en": FAQ_DATA_EN,
    "ru": FAQ_DATA_RU,
    "uz": FAQ_DATA_UZ,
}
END_MESSAGES = {
    "en": "That's all! Thank you!",
    "ru": "Это всё! Спасибо!",
    "uz": "Hammasi shu! Rahmat!",
}
# Can I help you with anything else? translations
ELSE_MESSAGES = {
    "en": "Can I help you with anything else?",
    "ru": "Могу ли я помочь вам с чем-нибудь еще?",
    "uz": "Yana biron narsa bilan yordam bera olamanmi?",
}

# Ask me a question from the menu: translations
MENU_MESSAGES = {
    "en": "Ask me a question from the menu:",
    "ru": "Задайте мне вопрос из меню:",
    "uz": "Menudan savol bering:",
}

# Start message: translations
START_MESSAGES = {
    "en": "Welcome to the TIAC Telegram Chat!",
}

# "I don't have an answer to this question, kindly send all other queries to info@tiac.uz and dbayzakova@tiac.uz and we will respond promptly." language based responses
FALLBACK_MESSAGES = {
    "en": "I don't have an answer to this question, kindly send all other queries to info@tiac.uz and bayzakova@tiac.uz and we will respond promptly.",
    "ru": "У меня нет ответа на этот вопрос, все остальные вопросы просим присылать на info@tiac.uz и bayzakova@tiac.uz и мы оперативно ответим.",
    "uz": "Bu savolga javobim yo'q, qolgan barcha so'rovlaringizni info@tiac.uz va bayzakova@tiac.uz manzillariga yuboring, biz zudlik bilan javob beramiz.",
}

WELCOME_MESSAGES = {
    "en": "You're welcome! Feel free to ask again if you have more questions.",
    "ru": "Пожалуйста! Не стесняйтесь спрашивать снова, если у вас есть еще вопросы.",
    "uz": "Arzimaydi! Agar boshqa savollaringiz bo'lsa, yana so'rashingiz mumkin.",
}

END_MESSAGE = "That's all! Thank you!"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await language_command(update, context)


async def questions_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_menu(update, context, MENU_MESSAGES.get(context.user_data.get("language", "en"), END_MESSAGE))


async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("English"), KeyboardButton("Русский"), KeyboardButton("O'zbekcha")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    if update.callback_query:
        await update.callback_query.message.reply_text(
        "To proceed, please selected desired language.\n\nЧтобы продолжить, выберите желаемую локаль.\n\nDavom etish uchun kerakli tilni tanlang.",
        reply_markup=reply_markup)
    else:
        await update.message.reply_text(
        "To proceed, please selected desired language.\n\nЧтобы продолжить, выберите желаемую локаль.\n\nDavom etish uchun kerakli tilni tanlang.",
        reply_markup=reply_markup)


async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language = update.message.text.lower()

    language_codes = {
        "english": "en",
        "русский": "ru",
        "o'zbekcha": "uz"
    }

    if language in language_codes:
        language_code = language_codes[language]
        context.user_data["language"] = language_code
        menu_message = MENU_MESSAGES.get(context.user_data.get("language", "en"), END_MESSAGE)
        if language_code == "en":
            await update.message.reply_text("Language set to English.")
        elif language_code == "ru":
            await update.message.reply_text("Язык установлен на русский.")
        elif language_code == "uz":
            await update.message.reply_text("Til o'zbek tiliga sozlandi.")

        await show_menu(update, context, menu_message)

    else:
        await update.message.reply_text("Invalid language selection. Please choose from the available options.")


async def answer_faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text
    end_message = END_MESSAGES.get(context.user_data.get("language", "en"), END_MESSAGE)
    else_message = ELSE_MESSAGES.get(context.user_data.get("language", "en"), END_MESSAGE)
    welcome_message = WELCOME_MESSAGES.get(context.user_data.get("language", "en"), END_MESSAGE)
    fallback_message = FALLBACK_MESSAGES.get(context.user_data.get("language", "en"), END_MESSAGE)

    if question == end_message:
        keyboard = [[InlineKeyboardButton("Questions", callback_data='/questions'),
                     InlineKeyboardButton("Language", callback_data='/language')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(welcome_message, reply_markup=reply_markup)

    else:
        faq_data = get_faq_data(context)
        answer = faq_data.get(question)
        if answer:
            await update.message.reply_text(answer)
            await show_menu(update, context, else_message)  # use else_message
        else:
            await update.message.reply_text(fallback_message)
            await show_menu(update, context, else_message)  # use else_message


async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, message_text):
    faq_data = get_faq_data(context)
    keyboard = [
        [KeyboardButton(question)] for question in faq_data.keys()
    ]
    keyboard.append([KeyboardButton(END_MESSAGES.get(context.user_data.get("language", "en"), END_MESSAGE))])

    reply_markup_sm = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    if update.callback_query:
        await update.callback_query.message.reply_text(text=message_text, reply_markup=reply_markup_sm)
    else:
        await update.message.reply_text(text=message_text, reply_markup=reply_markup_sm)


def get_faq_data(context: ContextTypes.DEFAULT_TYPE):
    language = context.user_data.get("language", "en")
    return FAQ_DATA.get(language, {})


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == '/questions':
        await questions_command(update, context)
    else:
        await language_command(update, context)


if __name__ == '__main__':
    application = ApplicationBuilder().token('7137950292:AAEfB0qjq9QuacocbVMYJZtQRqCl9ISThgg').build()

    start_handler = CommandHandler('start', start)
    questions_handler = CommandHandler('questions', questions_command)
    language_handler = CommandHandler('language', language_command)
    set_language_handler = MessageHandler(filters.Regex(r'^(English|Русский|O\'zbekcha)$'), set_language)
    answer_faq_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), answer_faq)  # modified handler
    button_callback_handler = CallbackQueryHandler(button)

    application.add_handler(start_handler)
    application.add_handler(questions_handler)
    application.add_handler(language_handler)
    application.add_handler(set_language_handler)
    application.add_handler(answer_faq_handler)
    application.add_handler(button_callback_handler)  # Add button handler

    application.run_polling()
