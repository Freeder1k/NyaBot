from dataclasses import dataclass

from niatypes.jsonableDataclass import JsonableDataclass


@dataclass(frozen=True)
class CharacterStats(JsonableDataclass):
    type: str
    nickname: str
    level: int
    xp: int
    xpPercent: int
    totalLevel: int
    wars: int
    playtime: int
    mobsKilled: int
    chestsFound: int
    blocksWalked: int
    itemsIdentified: int
    logins: int
    death: int
    discoveries: int

    @dataclass(frozen=True)
    class _Pvp(JsonableDataclass):
        kills: int
        deaths: int

    pvp: _Pvp
    gamemode: list[str]
    skillPoints: dict[str, int]

    @dataclass(frozen=True)
    class _Profession(JsonableDataclass):
        level: int
        xpPercent: int

    professions: dict[str, _Profession]

    @dataclass(frozen=True)
    class _Dungeons(JsonableDataclass):
        total: int
        list: dict[str, int]  # dungeon name: completions

    dungeons: _Dungeons

    @dataclass(frozen=True)
    class _Raids(JsonableDataclass):
        total: int
        list: dict[str, int]  # raid name: completions

    raids: _Raids
    quests: list[str]


@dataclass(frozen=True)
class PlayerStats(JsonableDataclass):
    username: str
    online: bool
    server: str
    uuid: str
    rank: str
    rankBadge: str  # URL to the badge SVG in the Wynncraft CDN (only path)

    @dataclass(frozen=True)
    class _LegacyRankColour(JsonableDataclass):
        main: str
        sub: str

    legacyRankColour: _LegacyRankColour
    shortenedRank: str
    supportRank: str
    firstJoin: str
    lastJoin: str
    playtime: int

    @dataclass(frozen=True)
    class _Guild(JsonableDataclass):
        name: str
        prefix: str
        rank: str
        rankStars: str

    guild: _Guild

    @dataclass(frozen=True)
    class _GlobalData(JsonableDataclass):
        wars: int
        totalLevels: int
        killedMobs: int
        chestsFound: int

        @dataclass(frozen=True)
        class _Dungeons(JsonableDataclass):
            total: int
            list: dict[str, int]  # dungeon name: completions

        dungeons: _Dungeons

        @dataclass(frozen=True)
        class _Raids(JsonableDataclass):
            total: int
            list: dict[str, int]  # raid name: completions

        raids: _Raids
        completedQuests: int

        @dataclass(frozen=True)
        class _Pvp(JsonableDataclass):
            kills: int
            deaths: int

        pvp: _Pvp

    globalData: _GlobalData

    @dataclass(frozen=True)
    class _ForumLink(JsonableDataclass):
        forumUsername: str
        forumId: int
        gameUsername: str

    forumLink: _ForumLink
    ranking: dict[str, int]  # ranking type: rank
    publicProfile: bool
    characters: dict[str, CharacterStats]


@dataclass(frozen=True)
class CharacterShort(JsonableDataclass):
    type: str
    nickname: str
    level: int
    xp: int
    xpPercent: int
    totalLevel: int
    gamemode: list[str]


@dataclass(frozen=True)
class AbilityMap(JsonableDataclass):
    pages: int

    @dataclass(frozen=True)
    class _AbilityMapPiece(JsonableDataclass):
        type: str

        @dataclass(frozen=True)
        class _Coordinates(JsonableDataclass):
            x: int
            y: int

        coordinates: _Coordinates

        @dataclass(frozen=True)
        class _Meta(JsonableDataclass):
            icon: str  # Minecraft legacy item id e.g. 275:67
            page: int
            id: str  # Internal id of the ability, abilities in AT response are refered by the same id

        meta: _Meta
        family: list[str]

    map: list[_AbilityMapPiece]