from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, \
    ReplyKeyboardMarkup, KeyboardButton

trailer_button = InlineKeyboardButton('Трейлер', callback_data='movie_watch_trailer')
director_button = InlineKeyboardButton('Режиссер', callback_data='movie_director')
actors_button = InlineKeyboardButton('Актерский состав', callback_data='movie_actors')
watch_button = InlineKeyboardButton('Где посмотреть?', callback_data='movie_watch')
movie_keyboard = InlineKeyboardMarkup() \
    .add(trailer_button) \
    .add(director_button) \
    .add(actors_button) \
    .add(watch_button)


# button_random_movie = KeyboardButton('Случайный фильм')
button_blog = KeyboardButton('Блог')
additional_func = ReplyKeyboardMarkup()\
    .add(button_blog)
