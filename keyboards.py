import csv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def inline_categories_extractor():
    category_list = []

    with open('categories.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            category_list.append([InlineKeyboardButton(row[0], callback_data=row[0])])
    return category_list


categories_markup = InlineKeyboardMarkup(

    inline_categories_extractor() +
    [
        [
         InlineKeyboardButton("Добавить категорию", callback_data="add"),
         InlineKeyboardButton("Удалить категорию", callback_data="dell")
        ],

        [InlineKeyboardButton("Назад", callback_data="back")],
    ]
)

startup_markup = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("Категории", callback_data="1"),
            InlineKeyboardButton("Расходы за n дней", callback_data="2"),
            InlineKeyboardButton("Удалить расходы", callback_data="3")
        ]
    ]
)

category_data_entry_markup = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("Ввести сумму", callback_data="add_expanse")],
        [InlineKeyboardButton("Отмена", callback_data="back")]
    ]
)

cancel_markup = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("Назад", callback_data="back")]
    ]
)

print(categories_markup)
