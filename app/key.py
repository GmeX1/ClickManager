from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardButton

main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='👤Профиль')],
                                     [KeyboardButton(text='🍉Запустить кликер на арбузы')],
                                     [KeyboardButton(text='🆘Помощь')],
                                     [KeyboardButton(text='⚙️Настройки кликера')]
                                     ],
                           resize_keyboard=True,
                           input_field_placeholder='Выберите действие')
OFF = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='⬅❌Выключить', callback_data='OFF')]
])
ON = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='⬅✅Включить', callback_data='ON')]
])

Settings = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Клики', callback_data='Klik')],
    [InlineKeyboardButton(text='Авто клики', callback_data='Avto_klik')],
    [InlineKeyboardButton(text='Энергия', callback_data='Energy')],
    [InlineKeyboardButton(text='Максимальный уровень прокачки', callback_data='Max_lvl')]
])
Yes_or_No_K = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='✅Включить', callback_data='YesK')],
    [InlineKeyboardButton(text='❌Выключить', callback_data='NoK')]
])
Yes_or_No_A = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='✅Включить', callback_data='YesA')],
    [InlineKeyboardButton(text='❌Выключить', callback_data='NoA')]
])
Yes_or_No_E = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='✅Включить', callback_data='YesE')],
    [InlineKeyboardButton(text='❌Выключить', callback_data='NoE')]
])
contact_btn = ReplyKeyboardBuilder().button(text='Предоставить контакт', request_contact=True).adjust(1).as_markup(
    resize_keyboard=True)
