import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext, ConversationHandler
import os

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_CHAT_IDS = os.getenv('ADMIN_CHAT_IDS').split(',')
WEBINAR_LINK = 'https://example.com'
EXPIRE_TIME = datetime.datetime(2025, 3, 10, 10, 0, 0)  # زمان دقیق پایان کارگاه (مثال)
user_data = {}

NAME, GRADE = range(2)

def start(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    if str(user_id) in ADMIN_CHAT_IDS:
        admin_menu(update, context)
    else:
        context.user_data['user_id'] = user_id
        update.message.reply_text("سلام! به بات گروه آموزشی پل خوش آمدید. 🌟 لطفاً اسمتون رو وارد کنید:")
        return NAME

def get_name(update: Update, context: CallbackContext):
    user_name = update.message.text
    user_id = context.user_data['user_id']
    user_data[user_id] = {'name': user_name}
    update.message.reply_text(f"مرسی {user_name}! لطفاً پایه تحصیلی خود را وارد کنید (راهنمایی، دهم، یازدهم، دوازدهم، غیره): 📚")
    return GRADE

def get_grade(update: Update, context: CallbackContext):
    user_grade = update.message.text
    user_id = context.user_data['user_id']
    user_data[user_id]['grade'] = user_grade
    user_data[user_id]['username'] = update.message.from_user.username

    keyboard = [
        [InlineKeyboardButton("📎 دریافت لینک کارگاه", callback_data='get_link')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        "مرسی! 🌟 روی دکمه زیر کلیک کنید تا لینک وبینار رو دریافت کنید:",
        reply_markup=reply_markup
    )
    return ConversationHandler.END

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.message.chat.id
    if query.data == 'get_link':
        current_time = datetime.datetime.now()
        if current_time < EXPIRE_TIME:
            query.edit_message_text(text=f"لینک کارگاه: [لینک موردنظر]({WEBINAR_LINK})")
        else:
            query.edit_message_text(text="زمان کارگاه موردنظر به پایان رسیده و لینک منقضی شده است. ⏰")
    elif query.data == 'admin_manage':
        admin_menu(update, context)
    elif query.data == 'manage_admins':
        manage_admins(update, context)
    elif query.data == 'workshop':
        workshop(update, context)
    elif query.data == 'support':
        support(update, context)
    elif query.data == 'anonymous':
        anonymous(update, context)
    elif query.data == 'schedule':
        schedule(update, context)
    elif query.data == 'back':
        menu(update, context)
    elif query.data == 'user_list':
        send_participants(update, context)

def menu(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("🎓 کارگاه", callback_data='workshop')],
        [InlineKeyboardButton("🛠 پشتیبانی", callback_data='support')],
        [InlineKeyboardButton("🔐 ارتباط ناشناس", callback_data='anonymous')],
        [InlineKeyboardButton("📅 برنامه", callback_data='schedule')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        "خدمات موجود رو انتخاب کنید:",
        reply_markup=reply_markup
    )

def workshop(update: Update, context: CallbackContext):
    current_time = datetime.datetime.now()
    if current_time < EXPIRE_TIME:
        update.callback_query.edit_message_text(text=f"زمان مانده به شروع کارگاه: {(EXPIRE_TIME - current_time).seconds // 60} دقیقه ⏳")
    else:
        update.callback_query.edit_message_text(text="قرار نیست کارگاهی برگزار بشه. 📅")

def support(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("ارتباط با آقای فلاح", url='https://t.me/username')],
        [InlineKeyboardButton("ارتباط با پشتیبانی گروه", url='https://t.me/username')],
        [InlineKeyboardButton("برگشت 🔙", callback_data='back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.edit_message_text(
        "یکی از گزینه‌های زیر رو انتخاب کنید:",
        reply_markup=reply_markup
    )

def anonymous(update: Update, context: CallbackContext):
    update.callback_query.edit_message_text("خیالت تخت خواب فنری! 🛌 پیامت رو تایپ کن و ارسال کن:")

def schedule(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("📚 برنامه درسی", callback_data='study_schedule')],
        [InlineKeyboardButton("🏋️‍♂️ برنامه ورزشی", callback_data='sports_schedule')],
        [InlineKeyboardButton("🥗 برنامه تغذیه", callback_data='nutrition_schedule')],
        [InlineKeyboardButton("برگشت 🔙", callback_data='back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.edit_message_text(
        "یکی از برنامه‌های زیر رو انتخاب کنید:",
        reply_markup=reply_markup
    )

def admin_menu(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("⚙️ تنظیم مدیریت", callback_data='manage_admins')],
        [InlineKeyboardButton("🎓 کارگاه", callback_data='workshop')],
        [InlineKeyboardButton("🔐 ارتباط ناشناس", callback_data='anonymous')],
        [InlineKeyboardButton("📅 برنامه", callback_data='schedule')],
        [InlineKeyboardButton("لیست کاربران 📋", callback_data='user_list')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        "منوی ادمین:",
        reply_markup=reply_markup
    )

def manage_admins(update: Update, context: CallbackContext):
    update.callback_query.edit_message_text(text="مدیریت ادمین‌ها: اینجا کدهای لازم برای افزودن/حذف ادمین‌ها رو اضافه کنید.")

def send_participants(update: Update, context: CallbackContext):
    participants = [f"نام: {data['name']}, پایه: {data['grade']}, نام کاربری: @{data['username']}" for data in user_data.values()]
    participant_list = "\n".join(participants)
    for admin_id in ADMIN_CHAT_IDS:
        context.bot.send_message(chat_id=admin_id, text=f"لیست شرکت‌کنندگان:\n{participant_list}")

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(Filters.text & ~Filters.command, get_name)],
            GRADE: [MessageHandler(Filters.text & ~Filters.command, get_grade)]
        },
        fallbacks=[CommandHandler('start', start)]
    )

    dp.add_handler(conv_handler)
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(CommandHandler("menu", menu))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
