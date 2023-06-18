from http import HTTPStatus

import aiohttp
from aiohttp import ClientSession

from api import rateLimit

_mojang_rate_limit = rateLimit.RateLimit(60, 1)
rateLimit.register_ratelimit(_mojang_rate_limit)
_usernames_rate_limit = rateLimit.RateLimit(20, 0)
rateLimit.register_ratelimit(_usernames_rate_limit)

_sessionserver_rate_limit = rateLimit.RateLimit(200, 1)
rateLimit.register_ratelimit(_sessionserver_rate_limit)

_mojang_api_session: ClientSession = None
_mojang_sessionserver_sesion: ClientSession = None


def format_uuid(uuid: str) -> str:
    """
    Add the "-" to a uuid.
    """
    return "-".join((uuid[:8], uuid[8:12], uuid[12:16], uuid[16:20], uuid[20:32]))


async def username_to_uuid(username: str) -> str | None:
    """
    Get the minecraft uuid of a user via the username.

    :return: None, if the name doesn't exist. The uuid without "-" otherwise.
    """
    with _mojang_rate_limit:
        async with _mojang_api_session.get(f"/users/profiles/minecraft/{username}") as resp:
            if resp.status == HTTPStatus.NOT_FOUND:
                return None

            resp.raise_for_status()

            if resp.status == HTTPStatus.NO_CONTENT:
                return None

            return (await resp.json())["id"]


async def usernames_to_uuids(usernames: list[str]) -> list[tuple[str, str]] | None:
    """
    Get the minecraft uuids of up to 10 users via the usernames.

    Any name that is under 25 characters and fits the regex ^(?=.*?(\w|^)(\w|$))((?![#&\\\|\/"])\w){1,25}$ will not trigger this error.

    :return: list of tuple of (case corrected username), (The uuid without "-") for each name that exists.
        or None if an error occurred.
    """
    if len(usernames) > 10:
        raise TypeError("usernames list can't contain more than 10 items!")

    with _usernames_rate_limit:
        async with _mojang_api_session.post(f"/profiles/minecraft", json=usernames) as resp:
            if resp.status == HTTPStatus.NOT_FOUND:
                return None

            resp.raise_for_status()

            if resp.status == HTTPStatus.NO_CONTENT:
                return None

            return [(player["name"], player["id"]) for player in await resp.json()]


async def uuid_to_username(uuid: str) -> str | None:
    """
    Get the minecraft username of a user via the uuid.

    :return: None, if the uuid doesn't exist. The username otherwise.
    """
    with _sessionserver_rate_limit:
        async with _mojang_sessionserver_sesion.get(f"/session/minecraft/profile/{uuid}") as resp:
            if resp.status == HTTPStatus.NOT_FOUND:
                return None

            resp.raise_for_status()

            if resp.status == HTTPStatus.NO_CONTENT:
                return None

            res = (await resp.json())["name"]


def uuid_to_avatar(uuid: str) -> str:
    """
    Get a crafatar url for the avatar of the uuid.
    """
    return f"https://crafatar.com/avatars/{uuid}?overlay=True"


async def init_session():
    global _mojang_api_session, _mojang_sessionserver_sesion
    _mojang_api_session = aiohttp.ClientSession("https://api.mojang.com")
    _mojang_sessionserver_sesion = aiohttp.ClientSession("https://sessionserver.mojang.com")


async def close():
    await _mojang_api_session.close()
    await _mojang_sessionserver_sesion.close()
