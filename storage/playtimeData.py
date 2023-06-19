import asyncio
from dataclasses import dataclass
from datetime import date, time, timezone, datetime

from discord.ext import tasks

import api.wynncraft.guild
import api.wynncraft.player
import player
from api import minecraft
from storage import manager
import traceback


@dataclass(frozen=True)
class Playtime:
    uuid: str
    day: str
    playtime: int


async def get_playtime(uuid: str, day: date) -> Playtime | None:
    uuid = uuid.replace("-", "").lower()

    cur = manager.get_cursor()
    res = await cur.execute("""
                SELECT * FROM playtimes
                WHERE uuid = ?
                AND day = ?
            """, (uuid, day))

    data = tuple(await res.fetchall())
    if len(data) == 0:
        return None

    return Playtime(**{k: data[0][k] for k in data[0].keys()})


async def get_all_playtimes(uuid: str) -> tuple[Playtime]:
    uuid = uuid.replace("-", "").lower()

    cur = manager.get_cursor()
    res = await cur.execute("""
                SELECT * FROM playtimes
                WHERE uuid = ?
                ORDER BY day
            """, (uuid,))

    return tuple(Playtime(data["uuid"], data["day"], data["playtime"]) for data in await res.fetchall())


async def set_playtime(uuid: str, day: date, playtime: int):
    uuid = uuid.replace("-", "").lower()

    con = manager.get_connection()
    cur = manager.get_cursor()
    await cur.execute("""
            REPLACE INTO playtimes VALUES (?, ?, ?)
        """, (uuid, day, playtime))

    await con.commit()


async def get_first_date_after(date_before: date) -> date | None:
    cur = manager.get_cursor()
    res = await cur.execute("""
                    SELECT min(day) FROM playtimes
                    WHERE day >= ?
                """, (date_before,))

    data = tuple(await res.fetchall())
    if len(data) == 0:
        return None
    if 'min(day)' not in data[0].keys():
        return None
    return data[0]['min(day)']


async def get_first_date_after_from_uuid(date_before: date, uuid: str) -> date | None:
    uuid = uuid.replace("-", "").lower()

    cur = manager.get_cursor()
    res = await cur.execute("""
                    SELECT min(day) FROM playtimes
                    WHERE uuid = ?
                    AND day >= ?
                """, (uuid, date_before))

    data = tuple(await res.fetchall())
    if len(data) == 0:
        return None
    if 'min(day)' not in data[0].keys():
        return None
    return data[0]['min(day)']


@tasks.loop(time=time(hour=0, minute=0, tzinfo=timezone.utc))
async def update_playtimes():
    try:
        nia = await api.wynncraft.guild.stats("Nerfuria")

        # players = await player.get_players(uuids=[m.uuid for m in nia.members])
        pstats: list[api.wynncraft.player.Stats] = await asyncio.gather(
            *(api.wynncraft.player.stats(m.uuid) for m in nia.members))

        today = datetime.now(timezone.utc).date()
        await asyncio.gather(*(set_playtime(stats.uuid, today, stats.meta.playtime) for stats in pstats))
    except Exception:
        traceback.print_exc()
