from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardButton

main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='👤Профиль')],
                                     [KeyboardButton(text='🍉Запустить кликер на арбузы')],
                                     [KeyboardButton(text='🆘Помощь')]
                                     ],
                           resize_keyboard=True,
                           input_field_placeholder='Выберите действие')
OFF = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='⬅❌Выключить', callback_data='OFF')]
])
ON = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='⬅✅Включить', callback_data='ON')]
])
contact_btn = ReplyKeyboardBuilder().button(text='Предоставить контакт', request_contact=True).adjust(1).as_markup(
    resize_keyboard=True)
