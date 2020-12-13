import typing as tp
import json
import aiohttp

from lib.config import google_url, google_headers


async def get_request_to_google_search(name: str, number_results: int = 10) -> tp.Any:
    """

    :param name:
    :param number_results:
    :return:
    """
    pass
    # TODO: вынести отдельно гугл поиск, тогда можно будет независимо искать ссылку и id
    query = "+".join(name.split()) + f"&num={number_results}"
    async with aiohttp.ClientSession() as session:
        async with session.request("GET", google_url + query, headers=google_headers) as resp:
            response = await resp.text()
            status_code = resp.status

    if status_code >= 400:
        raise RuntimeError
    return json.loads(response)['results']


def get_movie_kinopoisk_id(search_results: tp.List[tp.Any]) -> tp.Tuple[int, str]:
    """

    :param search_results:
    :return:
    """
    film_prefix = "kinopoisk.ru/film/"
    series_prefix = "kinopoisk.ru/series/"

    for result in search_results:
        current_link = result['link']
        if film_prefix in current_link:
            idx = current_link.find(film_prefix)
            pre_id = current_link[idx + len(film_prefix):]
            return int(pre_id[: pre_id.find("/")]), "movies"
        elif series_prefix in current_link:
            idx = current_link.find(series_prefix)
            pre_id = current_link[idx + len(series_prefix):]
            return int(pre_id[: pre_id.find("/")]), "tv-series"
    return -1, "not found"


def get_watch_link(search_results: tp.List[tp.Any]) -> tp.Optional[str]:
    """

    :param search_results:
    :return:
    """
    for result in search_results:
        movie_info = result['title'] + ' ' + result['description']
        movie_info = movie_info.lower()
        if ("смотреть" in movie_info and "онлайн" in movie_info) \
                or ("просмотр" in movie_info and "онлайн" in movie_info):
            return result['link']
