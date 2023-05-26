from typing import Final

import aiohttp

from api import rateLimit

HTTP_STATUS_NO_CONTENT: Final = 204

_mojang_rate_limit = rateLimit.RateLimit(600, 10)
rateLimit.add_ratelimit(_mojang_rate_limit)

_sessionserver_rate_limit = rateLimit.RateLimit(200, 1)
rateLimit.add_ratelimit(_sessionserver_rate_limit)

_mojang_api_session = aiohttp.ClientSession("https://api.mojang.com/users/profiles/minecraft/")
_mojang_sessionserver_sesion = aiohttp.ClientSession("https://sessionserver.mojang.com/session/minecraft/profile/")


def format_uuid(uuid: str) -> str:
    """
    Add the "-" to a uuid.
    """
    return "-".join((uuid[:8], uuid[8:12], uuid[12:16], uuid[16:20], uuid[20:32]))


async def username_to_uuid(username: str) -> str | None:
    """
    Get the minecraft username of a user via the uuid.

    :return: None, if the name doesn't exist. The uuid without "-" otherwise.
    """
    with _mojang_rate_limit:
        async with _mojang_api_session.get(username) as resp:
            if resp.status == HTTP_STATUS_NO_CONTENT:
                return None

            return (await resp.json())["id"]


async def uuid_to_username(uuid: str) -> str | None:
    """
    Get the minecraft uuid of a user via the username.

    :return: None, if the uuid doesn't exist. The username otherwise.
    """
    with _sessionserver_rate_limit:
        async with _mojang_sessionserver_sesion.get(uuid) as resp:
            if resp.status == HTTP_STATUS_NO_CONTENT:
                return None

            return (await resp.json())["name"]