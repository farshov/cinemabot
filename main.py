import aiohttp

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ParseMode

import json
import typing as tp
import random

from lib.config import BOT_TOKEN, google_url, google_headers, kinopoisk_cloud
import lib.keyboards as kb
from lib.utils import get_request_to_google_search, get_movie_kinopoisk_id, get_watch_link

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


LAST_ASKED_MOVIE: tp.Dict[int, tp.Dict[str, tp.Any]] = {}


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    greet_photo = "https://движениевместе.рф/800/600/https/s11.stc.all.kpcdn.net/share/i/4/1805959/inx960x640.jpg"
    await bot.send_photo(
        message.from_user.id,
        photo=greet_photo
    )

    text = "👋 Привет! Меня зовут *Леонардо ДеШадо*. Рад знакомству!\n"\
           "🎬 Кому как не мне разбираться в кино. Так что, мой юный друг, "\
           "можешь задавать любые вопросы о кинемотографе.\n" \
           "😊 Буду рад помочь!"
    await bot.send_message(
        message.from_user.id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=kb.additional_func,
    )


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    text = "👋 Эй, я Лео! Вижу, что ты немного заблудился. Давай расскажу, что я умею.\n" \
           "🔍 Я могу помочь в поиске информации о фильме, трейлера и даже могу подсказать, " \
           "где можно посмотреть его.\n" \
           "⌨️ Для этого просто введи название фильма, можно даже не точно или описательно, " \
           "если не помнишь название " \
           "(я использую поисквой движок от компании 🏢, которую нельзя называть. " \
           "Но иногда поиск все-таки подводит).\n" \
           "📌 Если той информации, что я покажу, " \
           "будет недостаточно, то можешь запросить дополнительную с помощью соответствующей кнопки.\n" \
           "✈️ Также снизу есть кнопка со ссылкой на мой блог, которая выдает случайный пост. " \
           "Подписка-лайки приветствуются!\n" \
           "😚 Всегда к твоим услугам, Лео!"
    await bot.send_message(
        message.from_user.id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=kb.additional_func,
    )


@dp.callback_query_handler(lambda c: c.data == 'movie_watch_trailer')
async def process_callback_button_movie_trailer(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    if callback_query.from_user.id not in LAST_ASKED_MOVIE:
        await bot.send_message(callback_query.from_user.id,
                               "😱 Прости, забыл, какой фильм мы обсуждаем. Напомни, пожалуйста",
                               reply_markup=kb.additional_func,
                               )
        return

    movie_info = LAST_ASKED_MOVIE[callback_query.from_user.id]
    if 'trailer' in movie_info and movie_info['trailer']:
        response = f"*Трейлер: * {movie_info['trailer']}"
        await bot.send_message(callback_query.from_user.id,
                               response,
                               parse_mode=ParseMode.MARKDOWN,
                               reply_markup=kb.additional_func,)
    else:
        await bot.send_message(callback_query.from_user.id,
                               "❌ Не нашел ничего по вашему запросу",
                               reply_markup=kb.additional_func,)


@dp.callback_query_handler(lambda c: c.data == 'movie_director')
async def process_callback_button_movie_director(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    if callback_query.from_user.id not in LAST_ASKED_MOVIE:
        await bot.send_message(callback_query.from_user.id,
                               "😱 Прости, забыл, какой фильм мы обсуждаем. Напомни, пожалуйста",
                               reply_markup=kb.additional_func,)
        return

    movie_info = LAST_ASKED_MOVIE[callback_query.from_user.id]
    if 'directors' not in movie_info or not len(movie_info['directors']):
        await bot.send_message(callback_query.from_user.id,
                               "❌ Не нашел ничего по вашему запросу",
                               reply_markup=kb.additional_func,)
        return
    if len(movie_info['directors']) == 1:
        response = f"*Режиссер:* {movie_info['directors'][0]}"
    else:
        response = f"*Режиссеры:* "
        for director in movie_info['directors'][:-1]:
            response += director + ", "
        response += movie_info['directors'][-1]
    await bot.send_message(callback_query.from_user.id, response,
                           parse_mode=ParseMode.MARKDOWN,
                           reply_markup=kb.additional_func,)


@dp.callback_query_handler(lambda c: c.data == 'movie_actors')
async def process_callback_button_movie_actors(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    if callback_query.from_user.id not in LAST_ASKED_MOVIE:
        await bot.send_message(callback_query.from_user.id,
                               "😱 Прости, забыл, какой фильм мы обсуждаем. Напомни, пожалуйста",
                               reply_markup=kb.additional_func,)
        return

    movie_info = LAST_ASKED_MOVIE[callback_query.from_user.id]
    if 'actors' not in movie_info or not len(movie_info['actors']):
        await bot.send_message(callback_query.from_user.id,
                               "❌ Не нашел ничего по вашему запросу",
                               reply_markup=kb.additional_func,)
        return

    response = f"*Актерский состав:* "
    for director in movie_info['actors'][:-1]:
        response += director + ", "
    response += movie_info['actors'][-1]
    await bot.send_message(callback_query.from_user.id, response,
                           parse_mode=ParseMode.MARKDOWN,)


@dp.callback_query_handler(lambda c: c.data == 'movie_watch')
async def process_callback_button_movie_watch(callback_query: types.CallbackQuery) -> None:
    await bot.answer_callback_query(callback_query.id)
    if callback_query.from_user.id not in LAST_ASKED_MOVIE:
        await bot.send_message(callback_query.from_user.id,
                               "😱 Прости, забыл, какой фильм мы обсуждаем. Напомни, пожалуйста",
                               reply_markup=kb.additional_func,)
        return

    movie_info = LAST_ASKED_MOVIE[callback_query.from_user.id]
    if 'watch_movie_link' not in movie_info or not len(movie_info['watch_movie_link']):
        await bot.send_message(callback_query.from_user.id,
                               "❌ Не нашел ничего по вашему запросу",
                               reply_markup=kb.additional_func,)
        return

    response = f"*Ссылка на просмотр:* " + movie_info['watch_movie_link']
    await bot.send_message(callback_query.from_user.id, response,
                           parse_mode=ParseMode.MARKDOWN,
                           reply_markup=kb.additional_func,)


@dp.message_handler(lambda x: x.text == "Блог")
async def process_random_movie_button(message: types.Message) -> None:
    imgs = {
        "Это я в Голливуде был, щас я дома уже.": "https://f10.pmo.ee/oy9hfQ3N-hEgCBgJJ26BZRTAcFE=/"
                                                  "1370x820/filters:focal(1642x298:2253x905)/nginx/o/"
                                                  "2020/01/20/12882968t1h1759.jpg",
        "Это я на охоте был, щас я дома уже.": "https://i.ytimg.com/vi/Zm8G8LwqVBc/maxresdefault.jpg",
        "Это я Aviasales рекламировал, щас я дома уже.": "https://avatars.mds.yandex.net/get-zen_doc/"
                                                         "1034365/pub_5bdd67c594c14900aa528f27_5bdd682"
                                                         "fe4c44c00aa0228ce/scale_1200",
        "Это я по алгосам отл получил, щас я дома уже.": "https://s0.rbk.ru/v6_top_pics/"
                                                         "media/img/8/87/754567222734878.jpg",
        "Это я по алгосам отл получил, щас я дома уже.": "https://s0.rbk.ru/v6_top_pics/"
                                                         "media/img/8/87/754567222734878.jpg",
        "Это я по алгосам отл получил, щас я дома уже.": "https://s0.rbk.ru/v6_top_pics/"
                                                         "media/img/8/87/754567222734878.jpg",
        "Это я миллиардером был, щас я дома уже.": "https://lh3.googleusercontent.com/proxy/"
                                                  "bViVwAv60qATjqRU5B-U_XmDtiw2GYLLYWGx0M9PbomE8sA_"
                                                  "0C4p7yw-Yt62DSPg0sqEzPjLEUmOO3fyXiAzDKfEMJMo3s4",
        "Это я на речке был, щас я дома уже.": "https://files.vm.ru/photo/vecherka/"
                                               "2017/12/doc6xt2ahmo2ex13whuj9z0_800_480.jpg",
        "Это я на диком западе был, щас я дома уже.": "https://regnum.ru/uploads/pictures/"
                                                      "news/2019/01/23/regnum_picture_1548221299149453_normal.jpg",
    }
    img_number = random.randint(0, len(imgs) - 1)
    caption = sorted(list(imgs.keys()))[img_number]
    await bot.send_photo(
        message.from_user.id,
        photo=imgs[caption],
        caption=caption,
        parse_mode=ParseMode.MARKDOWN,
    )


@dp.message_handler()
async def process_text(message: types.Message) -> None:
    try:
        search_results = await get_request_to_google_search(message.text + " кино")
    except RuntimeError:
        await bot.send_photo(
            message.from_user.id,
            photo="https://memepedia.ru/wp-content/uploads/2017/08/остров-проклятых-мем.jpg",
            caption="❌ Произошла ошибка при поиске",
        )
        return

    movie_id, genre = get_movie_kinopoisk_id(search_results)
    if movie_id == -1 and genre == "not found":
        await bot.send_photo(
            message.from_user.id,
            photo="https://memepedia.ru/wp-content/uploads/2017/08/остров-проклятых-мем.jpg",
            caption="❌ По вашему запросу не удалось ничего найти",
            reply_markup=kb.additional_func,
        )
        return

    request = f"https://api.kinopoisk.cloud/{genre}/{movie_id}/token/{kinopoisk_cloud}"
    async with aiohttp.ClientSession() as session:
        async with session.get(request) as resp:
            response = await resp.text()
            response_status = resp.status

    if response_status >= 400:
        await bot.send_message(
            message.from_user.id,
            text="❌ Не удалось найти фильм в базе",
            reply_markup=kb.additional_func,
        )
        return

    parsed = json.loads(response)

    watch_movie_link = get_watch_link(search_results)
    if watch_movie_link is not None:
        parsed['watch_movie_link'] = watch_movie_link

    LAST_ASKED_MOVIE[message.from_user.id] = parsed

    caption = ""
    if 'title' in parsed and parsed['title'] is not None:
        caption += f"✔️*Название*: {parsed['title']}\n"
    if 'year' in parsed and parsed['year'] is not None:
        caption += f"✔️*Год*: {parsed['year']}\n"
    if 'rating_kinopoisk' in parsed and parsed['rating_kinopoisk'] is not None:
        caption += f"✔️*Рейтинг Кинопоиск*: {parsed['rating_kinopoisk']}\n"
    if 'description' in parsed and parsed['description'] is not None:
        caption += f"✔️*Описание*: {parsed['description']}"

    if 'poster' in parsed and parsed['poster'] is not None:
        await bot.send_photo(
            message.from_user.id,
            photo=parsed['poster'][2:],
            caption=caption,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=kb.movie_keyboard,
        )
    elif caption:
        await bot.send_message(
            message.from_user.id,
            text=caption,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=kb.movie_keyboard,
        )
    else:
        await bot.send_message(
            message.from_user.id,
            text="❌ Не удалось найти фильм в базе",
            reply_markup=kb.additional_func,
        )

if __name__ == '__main__':
    executor.start_polling(dp)
