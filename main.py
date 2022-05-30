import time
import datetime
# import logging
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters  #, Updater
from telegram import Update #, Bot, InlineKeyboardButton, InlineKeyboardMarkup #,ReplyKeyboardMarkup, ReplyKeyboardRemove, Bot
from keyboards import *
#import random
#import re

# logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
# logger = logging.getLogger(__name__)

# aboba = ""   # (\/)(ಠ_ಠ)(\/)
STAGE = 0

MULTYPLIER_PAGES = 10


async def start(update: Update, context):
    user = update.message.from_user
    first_name = update.message.chat.first_name

    if user.id in [1137442897, 890981069, 5260146834]:

        per_month = cost_for_calculation(extractor_for_calculation(days_list_generator_for_calc(30)))
        per_week = cost_for_calculation(extractor_for_calculation(days_list_generator_for_calc(7)))

        if not per_month:

             await  update.message.reply_text(f"Привет {first_name}, приятно познакомиться с тобой!")

        elif per_month and not per_week:

            objects_per_month = [x + " : " + str(y) + "\n" for x, y in per_month.items()]

            await update.message.reply_text(
                f"Расходы за последние 30 дней составили:\n\n{''.join(objects_per_month)}\nИ суммарно выходит {sum(per_month.values())} лари.")

        else:

            objects_per_week = [x + " : " + str(y) + "\n" for x, y in per_week.items()]
            objects_per_month = [x + " : " + str(y) + "\n" for x, y in per_month.items()]
            await update.message.reply_text(
                f"Расходы за последние 7 дней составили:\n\n{''.join(objects_per_week)}\nИ суммарно выходит {sum(per_week.values())} лари.\n\n" +
                '-----------------------------------------\n\n' +
                f"Расходы за последние 30 дней составили:\n\n{''.join(objects_per_month)}\nИ суммарно выходит {sum(per_month.values())} лари.")

        await update.message.reply_text("Выберете раздел", reply_markup=startup_markup)

        return STAGE + 1


async def show_statistic(update: Update, context):

    per_month = cost_for_calculation(extractor_for_calculation(days_list_generator_for_calc(30)))
    per_week = cost_for_calculation(extractor_for_calculation(days_list_generator_for_calc(7)))

    if not per_month:

        pass

    elif per_month and not per_week:

        objects_per_month = [x + " : " + str(y) + "\n" for x, y in per_month.items()]

        await update.message.reply_text(
            f"Расходы за последние 30 дней составили:\n\n{''.join(objects_per_month)}\nИ суммарно выходит {sum(per_month.values())} лари.")

    else:

        objects_per_week = [x + " : " + str(y) + "\n" for x, y in per_week.items()]
        objects_per_month = [x + " : " + str(y) + "\n" for x, y in per_month.items()]
        await update.message.reply_text(
            f"Расходы за последние 7 дней составили:\n\n{''.join(objects_per_week)}\nИ суммарно выходит {sum(per_week.values())} лари.\n\n" +
            '-----------------------------------------\n\n' +
            f"Расходы за последние 30 дней составили:\n\n{''.join(objects_per_month)}\nИ суммарно выходит {sum(per_month.values())} лари.")

    await update.message.reply_text("Выберете раздел", reply_markup=startup_markup)

    return STAGE + 1


async def categories(update, context):
    query = update.callback_query

    await query.answer()
    await query.edit_message_text("Выберете категорию", reply_markup=categories_markup)
    return STAGE + 2


async def append_category(update, context):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Введите название категории.", reply_markup=cancel_markup)
    return STAGE + 5


async def writer_categories(update, context):

    message = str(update.message.text)

    await context.bot.delete_message(chat_id=update.message.chat.id, message_id=update.message.message_id)

    with open('categories.txt', 'a', encoding='utf-8') as f:
        f.write(message + '\n')

    global categories_markup

    categories_markup['inline_keyboard'].insert(0, [InlineKeyboardButton(message, callback_data=message)])

    await update.message.reply_text("Категория успешно добавленна, выберете раздел", reply_markup=startup_markup)
    return STAGE + 1


async def remove_categories(update, context):
    query = update.callback_query

    delete_categories_markup = InlineKeyboardMarkup(
        inline_categories_extractor() +
        [
            [InlineKeyboardButton("Назад", callback_data="back")],
        ]
    )

    await query.answer()
    await query.edit_message_text("Выберете категорию для её удаления.", reply_markup=delete_categories_markup)
    return STAGE + 6


async def deleter_categories(update, context):
    query = update.callback_query
    await query.answer()
    with open("categories.txt", "r", encoding='utf-8') as f:
        lines = f.readlines()
    with open("categories.txt", "w", encoding='utf-8') as f:
        for line in lines:
            if line.strip("\n") != query.data:
                f.write(line)

    global categories_markup

    categories_markup['inline_keyboard'].remove([InlineKeyboardButton(query.data, callback_data=query.data)])

    await query.edit_message_text("Категория успешно удаленна, выберете раздел", reply_markup=startup_markup)
    return STAGE + 1


async def add_value(update, context):
    query = update.callback_query
    context.user_data['category'] = query.data
    await query.answer()
    await query.edit_message_text(f"Выберете кнопку для {query.data.lower()}", reply_markup=category_data_entry_markup)
    return STAGE + 3


async def add_expense(update, context):
    query = update.callback_query
    await query.answer()
    # print(query.data)
    await query.edit_message_text("Введите расходы", reply_markup=cancel_markup)
    return STAGE + 3


async def asdel_expense(update, context):

    text = str(update.message.text)

    if is_float(text):
        write_row(context.user_data['category'], text)
        del context.user_data['category']
        await context.bot.delete_message(chat_id=update.message.chat.id, message_id=update.message.message_id)
        await update.message.reply_text("Данные успешно введены", reply_markup=startup_markup)
        return STAGE + 1

    else:
        await context.bot.delete_message(chat_id=update.message.chat.id, message_id=update.message.message_id)
        await update.message.reply_text("Вы должны вести число", reply_markup=cancel_markup)
        return STAGE + 3


async def entry_of_days(update, context):

    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Введите кол-во дней для расчета", reply_markup=cancel_markup)
    return STAGE + 10


async def calculation(update, context):

    message_text = update.message.text

    await context.bot.delete_message(chat_id=update.message.chat.id, message_id=update.message.message_id)

    dayz = check_on_number_for_calc(message_text)

    if not dayz:
        await update.message.reply_text("Вы должны вести число")
        return STAGE + 10

    else:
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

        await update.message.reply_text(f"Расход за {int(dayz)} дней составил:\n\n{''.join(show_objects)}Что суммарно выходит {summ} лари.",
                                  reply_markup=reply_markup)
        return STAGE + 11


async def remove_expenses(update, context):

    query = update.callback_query
    await query.answer()

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
        category, summ, time = mydata[row]
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
        await update.callback_query.edit_message_text(f"выбранно \n\n {show}", reply_markup=reply_markup)

    return STAGE + 11


async def del_expenses(update, context):
    query = update.callback_query
    await query.answer()

    result = select_deleter(context.user_data['selected_object'])

    if result:
        await back(update, context)
        await update.callback_query.edit_message_text('Данные успешно удаленны', reply_markup=startup_markup)
    else:
        raise EOFError

    context.user_data['selected_object'] = None
    context.user_data['selected_page'] = None

    return STAGE + 1


async def back(update, context):

    context.user_data['list_data_objects'] = None
    context.user_data['selected_page'] = None
    context.user_data['selected_object'] = None

    #update.callback_query.answer()
    await update.callback_query.edit_message_text("Выберете раздел", reply_markup=startup_markup)

    #update.callback_query.message.edit_text(f"back stage", reply_markup=first_keyboard())
    #start(update, context)
    return STAGE + 1


async def cancel(update, context):

    await update.callback_query.edit_message_text("Выберете катигорию", reply_markup=categories_markup)

    return STAGE + 2


async def stop(update: Update, context):
    """Cancels and ends the conversation."""
    user = update.message.from_user
    # logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        'stopped',
    )

    return ConversationHandler.END


async def you_are_dick(update, context):
    await update.message.reply_text('Ты хуй')


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


def write_row(category: str, sum: str, time_string=None) -> bool:   # Нужно добавить время(часы и минуты)
    try:

        if not time_string:
            time_string = time.strftime("%d:%m:%Y", time.localtime())

        if not isinstance(sum, str):
            sum = str(sum)

        with open("log.csv", "a", encoding='utf-8') as file:
            file_write = csv.writer(file, delimiter="|", lineterminator="\n")
            file_write.writerow([category, sum, time_string])

        return True
    except Exception as e:
        raise e


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


def check_on_number_for_calc(message_text):

    try:
        return float(message_text)
    except:
        return False


def is_float(value):
  try:
    float(value)
    return True
  except:
    return False


def main():

    TOKEN = "5323207728:AAGzOc7CZKGr0f-OPfjntqMiGCqdABC_x_E"

    application = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            STAGE + 1: [

                CallbackQueryHandler(categories, pattern="1"),
                CallbackQueryHandler(entry_of_days, pattern="2"),
                CommandHandler("dick", you_are_dick)
            ],
            STAGE + 2: [
                CallbackQueryHandler(back, pattern="back"),
                CallbackQueryHandler(append_category, pattern="add"),
                CallbackQueryHandler(remove_categories, pattern="dell"),
                CallbackQueryHandler(add_value)
            ],
            STAGE + 3: [
                CallbackQueryHandler(cancel, pattern="back"),
                CallbackQueryHandler(add_expense, pattern="add_expanse"),
                MessageHandler(filters.TEXT, asdel_expense),

            ],
            STAGE + 5: [
                CallbackQueryHandler(cancel, pattern="back"),
                MessageHandler(filters.TEXT, writer_categories)
            ],
            STAGE + 6: [
                CallbackQueryHandler(cancel, pattern="back"),
                CallbackQueryHandler(deleter_categories)
            ],
            STAGE + 10: [
                CallbackQueryHandler(back, pattern="back"),
                MessageHandler(filters.TEXT, calculation)
            ],
            STAGE + 11: [
                CallbackQueryHandler(back, pattern="back"),
                CallbackQueryHandler(del_expenses, pattern="del_expenses"),
                CallbackQueryHandler(remove_expenses)

            ]

        },
        fallbacks=[CommandHandler('stop', stop), CommandHandler('stat', show_statistic)], per_chat=False
    )

    application.add_handler(conv_handler)
    application.run_polling()



if __name__ == '__main__':
    main()