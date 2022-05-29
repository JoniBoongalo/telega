import csv
import time
import datetime
import logging
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup #,ReplyKeyboardMarkup, ReplyKeyboardRemove, Bot
#import random
#import re

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

aboba = ""   # (\/)(ಠ_ಠ)(\/)
STAGE = 0

MULTYPLIER_PAGES = 10


def first_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("Категории", callback_data="1"),
            InlineKeyboardButton("Расходы за n дней", callback_data="2"),
            InlineKeyboardButton("Удалить расходы", callback_data="3")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    return reply_markup


def categories_keyboard():
    categories_dict = opener_for_categories_keyboard()
    keyboard = []
    keyboard_add = {
        "Добавить категорию": "add",
        "Удалить категорию": "dell",
        "Назад": "back"
    }

    for i in categories_dict.items():
        keyboard.append([InlineKeyboardButton(i[0], callback_data=i[1])])

    for x in keyboard_add.items():
        keyboard.append([InlineKeyboardButton(x[0], callback_data=x[1])])

    '''keyboard = [ # Примерно так выглядит эта переменная 
            [InlineKeyboardButton("Аренда жилья", callback_data="Аренда жилья")],
            [InlineKeyboardButton("Еда", callback_data="Еда")],
            [InlineKeyboardButton("Комуналка", callback_data="Комуналка")],
            [InlineKeyboardButton("Такси", callback_data="Такси")],
            [InlineKeyboardButton("Мобильный интернет", callback_data="Мобильный интернет")],
            [InlineKeyboardButton("Прочее", callback_data="Прочее")],
            [InlineKeyboardButton("Назад", callback_data="back")]
    ]'''

    reply_markup = InlineKeyboardMarkup(keyboard)

    return reply_markup


def opener_for_categories_keyboard():
    d = {}

    with open('categories.txt', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            d.setdefault(row[0], row[0])
    return d


def category_data_entry():
    keyboard = [
        [InlineKeyboardButton("Ввести сумму", callback_data="1")],
        [InlineKeyboardButton("Отмена", callback_data="cancel")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    return reply_markup


def start(update, context):

    user = update.message.from_user

    first_name = update.message.chat.first_name
    context.user_data["name"] = first_name
    context.user_data['len'] = 0

    if user.id in [1137442897, 890981069, 5260146834]:
        # days_generator = days_list_generator_for_calc(30)
        # ext = extractor_for_calculation(days_generator)
        # keys = cost_for_calculation(ext)

        per_month = cost_for_calculation(extractor_for_calculation(days_list_generator_for_calc(30)))

        per_week = cost_for_calculation(extractor_for_calculation(days_list_generator_for_calc(7)))
        # print(days_generator)
        # print(ext)
        # print(keys)
        if not per_month:

            update.message.reply_text(f"Привет {first_name}, приятно познакомиться с тобой!")

        elif per_month and not per_week:

            update.message.reply_text(f"Привет {first_name}!")

            summ = sum(per_month.values())
            show_objects = [x + " : " + str(y) + "\n" for x, y in per_month.items()]

            update.message.reply_text(
                f"Расходы за последние 30 дней составили:\n\n{''.join(show_objects)}\nИ суммарно выходит {summ} лари.")

        else:

            update.message.reply_text(f"Привет {first_name}!")

            summ = sum(per_week.values())
            show_objects = [x + " : " + str(y) + "\n" for x, y in per_week.items()]
            update.message.reply_text(
                f"Расходы за последние 7 дней составили:\n\n{''.join(show_objects)}\nИ суммарно выходит {summ} лари.")

            summ = sum(per_month.values())
            show_objects = [x + " : " + str(y) + "\n" for x, y in per_month.items()]
            update.message.reply_text(
                f"Расходы за последние 30 дней составили:\n\n{''.join(show_objects)}\nИ суммарно выходит {summ} лари.")

        update.message.reply_text("Выберете раздел", reply_markup=first_keyboard())

        return STAGE + 1


def categories(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text("Выберете катигорию", reply_markup=categories_keyboard())
    return STAGE + 2


def add_value(update, context):
    global aboba

    categories_dict = opener_for_categories_keyboard()
    query = update.callback_query
    query.answer()

    for key, value in categories_dict.items():
        if value == query.data:
            aboba += value

    query.edit_message_text(f"Выберете кнопку для {query.data.lower()}", reply_markup=category_data_entry())
    return STAGE + 3


def entry_of_expenses(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text("Введите расходы")
    return STAGE + 4


def add_categories(update, context):
    query = update.callback_query
    query.answer()

    button = [
        [InlineKeyboardButton("Назад", callback_data="cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(button)

    query.edit_message_text("Введите название категории.", reply_markup=reply_markup)
    return STAGE + 5


def writer_categories(update, context):
    message = str(update.message.text)

    with open('categories.txt', 'a', encoding='utf-8') as f:
        f.write(message + '\n')

    update.message.reply_text("Категория успешно добавленна, выберете раздел", reply_markup=first_keyboard())
    return STAGE + 1


def remove_categories(update, context):
    query = update.callback_query
    query.answer()
    # Это говнище должно выводить все категории виде кнопок
    buttons = opener_for_categories_keyboard()

    keyboard = [[InlineKeyboardButton(x[0], callback_data=x[1])] for x in buttons.items()]
    keyboard.append([InlineKeyboardButton("Назад", callback_data="cancel")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text("Выберете категорию для её удаления.", reply_markup=reply_markup)
    return STAGE + 6


def deleter_categories(update, context):
    query = update.callback_query
    query.answer()

    categories_dict = opener_for_categories_keyboard()

    with open('categories.txt', 'w', encoding='utf-8') as f:
        for i in categories_dict:
            if not query.data == i:
                f.write(i + '\n')

    query.edit_message_text("Категория успешно удаленна, выберете раздел", reply_markup=first_keyboard())
    return STAGE + 1


def entry_of_days(update, context):

    button = [
        [InlineKeyboardButton("Назад", callback_data="back")]
        #[InlineKeyboardButton("Удалить расходы", callback_data="del")]
    ]
    reply_markup = InlineKeyboardMarkup(button)

    query = update.callback_query
    query.answer()
    query.edit_message_text("Введите кол-во дней для расчета", reply_markup=reply_markup)
    return STAGE + 10


def back(update, context):

    context.user_data['list_data_objects'] = None
    context.user_data['selected_page'] = None

    #update.callback_query.answer()
    update.callback_query.edit_message_text("Выберете раздел", reply_markup=first_keyboard())

    #update.callback_query.message.edit_text(f"back stage", reply_markup=first_keyboard())
    #start(update, context)
    return STAGE + 1


def cancel(update, context):

    update.callback_query.edit_message_text("Выберете катигорию", reply_markup=categories_keyboard())

    return STAGE + 2


def stop(update: Update, context):
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'stopped',
    )

    return ConversationHandler.END


def writer(update, context):
    global aboba
    named_tuple = time.localtime()
    time_string = time.strftime("%d:%m:%Y", named_tuple)

    categories = aboba

    if not check_on_number_for_calc(update.message.text):
        update.message.reply_text("Вы должны вести число")
        return STAGE + 4

    sum = str(update.message.text)

    with open("log.csv", "a", encoding='utf-8') as file:
        file_write = csv.writer(file, delimiter="|", lineterminator="\n")
        file_write.writerow([categories, sum, time_string])

    aboba = ""

    update.message.reply_text("Данные успешно введены", reply_markup=first_keyboard())
    return STAGE + 1


def calculation(update, context):

    message_text = update.message.text

    dayz = check_on_number_for_calc(message_text)

    if not dayz:
        update.message.reply_text("Вы должны вести число")
        return STAGE + 10

    days_list = days_list_generator_for_calc(dayz)

    list_data_objects = extractor_for_calculation(days_list)
    # для следующего стейджа
    context.user_data['list_data_objects'] = list_data_objects

    all_cost = cost_for_calculation(list_data_objects)


    summ = sum(all_cost.values())
    show_objects = [x + " : " + str(y) + "\n\n" for x, y in all_cost.items()]


    button = [
        [InlineKeyboardButton("Назад", callback_data="back")],
        [InlineKeyboardButton(f"Удалить расходы за {int(dayz)} дней", callback_data="delete")]
    ]
    reply_markup = InlineKeyboardMarkup(button)

    update.message.reply_text(f"Расход за {int(dayz)} дней составил:\n\n{''.join(show_objects)}Что суммарно выходит {summ} лари.",
                              reply_markup=reply_markup)
    return STAGE + 11


def check_on_number_for_calc(message_text):

    try:
        return float(message_text)
    except:
        return False


def days_list_generator_for_calc(days_num):

    dayz_list = []
    # составление списка дат
    for delta_day in range(int(days_num)):
        date = datetime.date.today() - datetime.timedelta(days=delta_day)
        dayz_list.append([date.day, date.month, date.year])

    return dayz_list


def extractor_for_calculation(dayz_list):

    new_list = []

    with open("log.csv", encoding="utf-8") as f:

        reader = csv.DictReader(f, delimiter="|")
        # Запись всех дней
        for row in reader:
            # конвертирование str из csv файла в struct object
            s = time.strptime(row['time_string'], "%d:%m:%Y")
            #  проверка на вхождение
            if [s.tm_mday, s.tm_mon, s.tm_year] in dayz_list:
                new_list.append((row['categories'], row['sum'], row['time_string']))

    return new_list


def cost_for_calculation(new_list):

    g = {}

    for i in new_list:  # Избавляемся от ненужных категорий и прибавляем к уже имеющимся категориям
        if not g.get(i[0]):
            g[i[0]] = float(i[1])

        else:
            g[i[0]] = g.get(i[0]) + float(i[1])

    return g


def remove_expenses_1(update, context):

    query = update.callback_query
    query.answer()

    # data = context.user_data['list_data_objects']

    show = ''

    if not context.user_data.get('selected_page'):
        context.user_data['selected_page'] = 0

    tmp_page = context.user_data['selected_page']

    if query.data == 'left_page' and context.user_data['selected_page'] > 0:
        context.user_data['selected_page'] -= 1
    elif query.data == 'right_page' and len(context.user_data['list_data_objects'][context.user_data['selected_page'] * MULTYPLIER_PAGES:context.user_data['selected_page'] * MULTYPLIER_PAGES + MULTYPLIER_PAGES:]) == 10:
        context.user_data['selected_page'] += 1
    elif query.data.isnumeric():
        if len(context.user_data['list_data_objects']) > 0:
            context.user_data['selected_object'].append(context.user_data['list_data_objects'][int(query.data)])
            del context.user_data['list_data_objects'][int(query.data)]

    page = context.user_data['selected_page']

    data = context.user_data['list_data_objects']
    mydata = context.user_data['list_data_objects'][page * MULTYPLIER_PAGES:page * MULTYPLIER_PAGES + MULTYPLIER_PAGES:]

    if not context.user_data.get('selected_object'):
        context.user_data['selected_object'] = []
    else:
        for element in context.user_data['selected_object']:
            show = show + element[0] + ', ' + element[1] + ' лари, ' + element[2] + '\n'

    keyboard = []

    for row in range(len(mydata)):
        category, summ, time = data[row]
        keyboard.append([InlineKeyboardButton(f'{category}, {summ} лари, {time}',
                                              callback_data=str(row + (page * MULTYPLIER_PAGES)))])

    keyboard.append([InlineKeyboardButton('<', callback_data='left_page'),
                     InlineKeyboardButton(f"{page}", callback_data='NOT_USED'),
                     InlineKeyboardButton('>', callback_data='right_page')], )

    if context.user_data['selected_object']:
        keyboard.append([InlineKeyboardButton('удалить', callback_data='del_expenses')])

    # KTTC вести эту хуйню выше
    keyboard.append([InlineKeyboardButton("Назад", callback_data="back")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    if (query.data not in ['left_page', 'right_page'] or context.user_data['selected_page'] != tmp_page) and query.data != 'NOT_USED':
        update.callback_query.edit_message_text(f"выбранно \n\n {show}", reply_markup=reply_markup)

    return STAGE + 11


def del_expenses(update, context):
    query = update.callback_query
    query.answer()

    result = select_deleter(context.user_data['selected_object'])

    if result:
        back(update, context)
        update.callback_query.edit_message_text('Данные успешно удаленны', reply_markup=first_keyboard())
    else:
        raise EOFError

    context.user_data['selected_object'] = None
    context.user_data['selected_page'] = None

    return STAGE + 1


def select_deleter(selected_object):

    log_csv = []

    try:

        with open("log.csv", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="|")
            for row in reader:
                log_csv.append((row['categories'], row['sum'], row['time_string']))

        with open("log.csv", "w", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter="|", lineterminator="\n")
            writer.writerow(('categories', 'sum', 'time_string'))
            for line in log_csv:
                if line not in selected_object:
                    writer.writerow(line)

        today = datetime.date.today()

        with open(f"deleted/{today.day}_{today.month}_{today.year}.csv", "a", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter="|", lineterminator="\n")
            for line in selected_object:
                writer.writerow(line)

        return True

    except:

        return False


def you_are_dick(update, context):
    update.message.reply_text('Ты хуй')


def main():
    TOKEN = "5323207728:AAGzOc7CZKGr0f-OPfjntqMiGCqdABC_x_E"
    # create the updater, that will automatically create also a dispatcher and a queue to
    # make them dialoge
    # updater = Updater(TOKEN, use_context=True)
    application = ApplicationBuilder().token("TOKEN").build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            # GENDER: [MessageHandler(Filters.regex('^(Boy|Girl|Other)$'), gender)],
            STAGE + 1: [
                # CallbackQueryHandler(button_stage1),
                # CommandHandler('start', start)
                CallbackQueryHandler(categories, pattern="1"),
                CallbackQueryHandler(entry_of_days, pattern="2"),
                CommandHandler("dick", you_are_dick)
                # CallbackQueryHandler(two, pattern="^" + str(TWO) + "$"),
                # CallbackQueryHandler(three, pattern="^" + str(THREE) + "$"),
                # CallbackQueryHandler(four, pattern="^" + str(FOUR) + "$"),
            ],
            STAGE + 2: [
                CallbackQueryHandler(back, pattern="back"),
                CallbackQueryHandler(add_categories, pattern="add"),
                CallbackQueryHandler(remove_categories, pattern="dell"),
                CallbackQueryHandler(add_value)
                # CallbackQueryHandler(back, pattern="back")
            ],
            STAGE + 3: [
                CallbackQueryHandler(entry_of_expenses, pattern="1"),
                CallbackQueryHandler(cancel, pattern="cancel")
            ],
            STAGE + 4: [
                MessageHandler(Filters.text, writer)
            ],
            STAGE + 5: [
                CallbackQueryHandler(cancel, pattern="cancel"),
                MessageHandler(Filters.text, writer_categories)
            ],
            STAGE + 6: [
                CallbackQueryHandler(cancel, pattern="cancel"),
                CallbackQueryHandler(deleter_categories)
            ],
            # Расходы за n дней
            STAGE + 10: [
                CallbackQueryHandler(back, pattern="back"),
                MessageHandler(Filters.text, calculation)
            ],
            STAGE + 11: [
                CallbackQueryHandler(back, pattern="back"),
                CallbackQueryHandler(del_expenses, pattern="del_expenses"),
                CallbackQueryHandler(remove_expenses_1)

            ]

        },
        fallbacks=[CommandHandler('stop', stop)], per_chat=False
    )

    dispatcher = updater.dispatcher
    # add handlers for start and help commands
    dispatcher.add_handler(conv_handler)
    # dispatcher.add_handler(CommandHandler("start", start))
    # dispatcher.add_handler(CallbackQueryHandler(button_stage1))
    # start your shiny new bot
    updater.start_polling()
    # run the bot until Ctrl-C
    updater.idle()


if __name__ == '__main__':
    main()