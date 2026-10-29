"""Game manager: holds all games and scores, and enforces the rules."""

from __future__ import annotations

from collections.abc import Callable
import logging
import random
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from . import game as g
from .const import (
    CONF_LIGHTNING_BONUS,
    CONF_LIGHTNING_MOVES,
    CONF_NOTIFY,
    CONF_PLAYERS,
    CONF_POINTS_DRAW,
    CONF_POINTS_WIN,
    DEFAULT_LIGHTNING_BONUS,
    DEFAULT_LIGHTNING_MOVES,
    DEFAULT_POINTS_DRAW,
    DEFAULT_POINTS_WIN,
    DOMAIN,
    NO_NOTIFY,
    PANEL_URL_PATH,
    RESULT_DRAW,
    STATUS_FINISHED,
    STATUS_NONE,
    STATUS_PLAYING,
)

_LOGGER = logging.getLogger(__name__)

STORAGE_VERSION = 1

MESSAGES = {
    "nb": {
        "your_turn": "Din tur mot {name}! 🎯",
        "challenged_you_start": "{name} utfordrer deg! Du begynner 🎯",
        "challenged_they_start": "{name} utfordrer deg! {name} begynner.",
        "new_game_you_start": "Nytt parti mot {name}. Du begynner 🎯",
        "won": "{winner} vant over {loser} på {moves} trekk! 🏆 +{points} poeng",
        "won_lightning": "{winner} vant over {loser} på {moves} trekk! ⚡ Lynseier: +{points} poeng",
        "draw": "Uavgjort mellom {winner} og {loser}! 🤝",
        "resigned": "{loser} ga opp – {winner} vinner! 🏳️",
        "title": "🔴🟡 4 på rad",
    },
    "en": {
        "your_turn": "Your turn against {name}! 🎯",
        "challenged_you_start": "{name} challenges you! You start 🎯",
        "challenged_they_start": "{name} challenges you! {name} starts.",
        "new_game_you_start": "New game against {name}. You start 🎯",
        "won": "{winner} beat {loser} in {moves} moves! 🏆 +{points} points",
        "won_lightning": "{winner} beat {loser} in {moves} moves! ⚡ Lightning win: +{points} points",
        "draw": "Draw between {winner} and {loser}! 🤝",
        "resigned": "{loser} resigned – {winner} wins! 🏳️",
        "title": "🔴🟡 Connect Four",
    },
}


def game_id_for(person_a: str, person_b: str) -> str:
    """Return the stable id for the game between two persons."""
    first, second = sorted((person_a, person_b))
    return f"{first.split('.', 1)[1]}__{second.split('.', 1)[1]}"


class FireParadManager:
    """Owns the persisted state of all games and scores."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self._store: Store[dict[str, Any]] = Store(hass, STORAGE_VERSION, f"{DOMAIN}.{entry.entry_id}")
        self.data: dict[str, Any] = {"games": {}, "stats": {}, "total": 0, "last_result": "", "notify": True}
        self._listeners: list[Callable[[], None]] = []

    async def async_load(self) -> None:
        """Load persisted games and scores."""
        if stored := await self._store.async_load():
            self.data.update(stored)

    # --- configuration -------------------------------------------------

    @property
    def players(self) -> list[str]:
        return list(self.entry.options.get(CONF_PLAYERS, []))

    def _opt(self, key: str, default: int) -> int:
        return int(self.entry.options.get(key, default))

    @property
    def lang(self) -> str:
        return "nb" if (self.hass.config.language or "").split("-")[0] in ("nb", "no", "nn") else "en"

    def name(self, person: str) -> str:
        """Return a person's first name."""
        state = self.hass.states.get(person)
        full = state.name if state else person.split(".", 1)[-1].replace("_", " ").title()
        return full.split(" ")[0]

    def person_for_user(self, user_id: str | None) -> str | None:
        """Return the person entity linked to a user id."""
        if not user_id:
            return None
        for state in self.hass.states.async_all("person"):
            if state.attributes.get("user_id") == user_id:
                return state.entity_id
        return None

    @property
    def notify_enabled(self) -> bool:
        return bool(self.data.get("notify", True))

    async def async_set_notify(self, enabled: bool) -> None:
        self.data["notify"] = enabled
        self._changed()

    # --- listeners / persistence --------------------------------------

    @callback
    def async_add_listener(self, update: Callable[[], None]) -> Callable[[], None]:
        self._listeners.append(update)
        return lambda: self._listeners.remove(update)

    def _changed(self) -> None:
        self._store.async_delay_save(lambda: self.data, 1)
        for update in list(self._listeners):
            update()

    # --- read helpers ---------------------------------------------------

    def stats(self, person: str) -> dict[str, int]:
        return self.data["stats"].setdefault(person, {"wins": 0, "draws": 0, "losses": 0, "points": 0})

    def game(self, game_id: str) -> dict[str, Any] | None:
        return self.data["games"].get(game_id)

    def active_player(self, game: dict[str, Any]) -> str:
        return game["p1"] if game["turn"] == 1 else game["p2"]

    def _require_game(self, game_id: str) -> dict[str, Any]:
        game = self.game(game_id)
        if game is None or game["p1"] not in self.players or game["p2"] not in self.players:
            raise ServiceValidationError(translation_domain=DOMAIN, translation_key="unknown_game", translation_placeholders={"game_id": game_id})
        return game

    def _check_caller(self, game: dict[str, Any], caller: str | None) -> None:
        """Players logged in as themselves may only act in their own games on their turn."""
        if caller is None or caller not in self.players:
            return
        if caller not in (game["p1"], game["p2"]):
            raise ServiceValidationError(translation_domain=DOMAIN, translation_key="not_your_game")

    # --- actions --------------------------------------------------------

    async def async_start(self, user_id: str | None, opponent: str, player: str | None = None) -> str:
        """Start a game. A logged-in player challenges `opponent`; otherwise `player` must be given."""
        caller = self.person_for_user(user_id)
        challenger = caller if caller in self.players else player
        if challenger is None or challenger not in self.players or opponent not in self.players or challenger == opponent:
            raise ServiceValidationError(translation_domain=DOMAIN, translation_key="invalid_players")

        game_id = game_id_for(challenger, opponent)
        p1, p2 = sorted((challenger, opponent))
        game = self.data["games"].setdefault(game_id, {"p1": p1, "p2": p2, "wins1": 0, "wins2": 0, "draws": 0})
        if game.get("status") == STATUS_PLAYING:
            return game_id

        now = dt_util.utcnow().isoformat()
        game.update(
            board=g.new_board(), turn=random.choice((1, 2)), status=STATUS_PLAYING, win=[], last=-1,
            result="", moves=0, started=now, updated=now,
        )
        self._changed()

        starter = self.active_player(game)
        if caller in (p1, p2):
            other = p2 if caller == p1 else p1
            key = "challenged_you_start" if starter == other else "challenged_they_start"
            await self._notify(other, key, game_id, name=self.name(caller))
        else:
            other = p2 if starter == p1 else p1
            await self._notify(starter, "new_game_you_start", game_id, name=self.name(other))
        return game_id

    async def async_drop(self, user_id: str | None, game_id: str, column: int) -> None:
        """Drop the active player's piece in a column."""
        game = self._require_game(game_id)
        if game.get("status") != STATUS_PLAYING:
            raise ServiceValidationError(translation_domain=DOMAIN, translation_key="not_playing")
        caller = self.person_for_user(user_id)
        self._check_caller(game, caller)
        active = self.active_player(game)
        if caller in (game["p1"], game["p2"]) and caller != active:
            raise ServiceValidationError(translation_domain=DOMAIN, translation_key="not_your_turn", translation_placeholders={"name": self.name(active)})

        idx = g.landing_index(game["board"], column)
        if idx is None:
            raise ServiceValidationError(translation_domain=DOMAIN, translation_key="column_full")

        piece = g.PIECES[game["turn"]]
        game["board"] = g.place(game["board"], idx, piece)
        game["last"] = idx
        game["moves"] = game.get("moves", 0) + 1
        game["updated"] = dt_util.utcnow().isoformat()
        opponent = game["p2"] if active == game["p1"] else game["p1"]

        if line := g.winning_line(game["board"], idx):
            game["win"] = line
            await self._finish(game, game_id, winner=active, loser=opponent, how="won", moves=game["board"].count(piece))
        elif g.is_full(game["board"]):
            await self._finish(game, game_id, winner=active, loser=opponent, how="draw")
        else:
            game["turn"] = 2 if game["turn"] == 1 else 1
            self._changed()
            await self._notify(opponent, "your_turn", game_id, name=self.name(active))

    async def async_resign(self, user_id: str | None, game_id: str) -> None:
        """Resign (or cancel if fewer than two pieces have been played)."""
        game = self._require_game(game_id)
        if game.get("status") != STATUS_PLAYING:
            raise ServiceValidationError(translation_domain=DOMAIN, translation_key="not_playing")
        caller = self.person_for_user(user_id)
        self._check_caller(game, caller)
        if game.get("moves", 0) < 2:
            game.update(status=STATUS_NONE, updated=dt_util.utcnow().isoformat())
            self._changed()
            return
        loser = caller if caller in (game["p1"], game["p2"]) else self.active_player(game)
        winner = game["p2"] if loser == game["p1"] else game["p1"]
        await self._finish(game, game_id, winner=winner, loser=loser, how="resigned")

    async def async_reset(self) -> None:
        """Reset all scores, series and games."""
        self.data.update(games={}, stats={}, total=0, last_result="")
        self._changed()

    async def _finish(self, game: dict[str, Any], game_id: str, *, winner: str, loser: str, how: str, moves: int = 0) -> None:
        game["status"] = STATUS_FINISHED
        game["updated"] = dt_util.utcnow().isoformat()
        w, l = self.stats(winner), self.stats(loser)
        names = {"winner": self.name(winner), "loser": self.name(loser)}
        if how == "draw":
            game["result"] = RESULT_DRAW
            game["draws"] = game.get("draws", 0) + 1
            draw_points = self._opt(CONF_POINTS_DRAW, DEFAULT_POINTS_DRAW)
            for s in (w, l):
                s["draws"] += 1
                s["points"] += draw_points
            key, points = "draw", draw_points
        else:
            game["result"] = "1" if winner == game["p1"] else "2"
            game["wins1" if winner == game["p1"] else "wins2"] += 1
            points = self._opt(CONF_POINTS_WIN, DEFAULT_POINTS_WIN)
            key = how
            if how == "won" and moves <= self._opt(CONF_LIGHTNING_MOVES, DEFAULT_LIGHTNING_MOVES):
                points += self._opt(CONF_LIGHTNING_BONUS, DEFAULT_LIGHTNING_BONUS)
                key = "won_lightning"
            w["wins"] += 1
            w["points"] += points
            l["losses"] += 1
        self.data["total"] = self.data.get("total", 0) + 1
        message = MESSAGES[self.lang][key].format(points=points, moves=moves, **names)
        self.data["last_result"] = message
        self._changed()
        for person in (winner, loser):
            await self._notify_text(person, message, game_id)

    # --- notifications --------------------------------------------------

    async def _notify(self, person: str, key: str, game_id: str, **fmt: Any) -> None:
        await self._notify_text(person, MESSAGES[self.lang][key].format(**fmt), game_id)

    async def _notify_text(self, person: str, message: str, game_id: str) -> None:
        if not self.notify_enabled:
            return
        service = self.entry.options.get(CONF_NOTIFY, {}).get(person, NO_NOTIFY)
        if not service or service == NO_NOTIFY or "." not in service:
            return
        domain, name = service.split(".", 1)
        url = f"/{PANEL_URL_PATH}?game={game_id}"
        try:
            await self.hass.services.async_call(
                domain, name,
                {"title": MESSAGES[self.lang]["title"], "message": message,
                 "data": {"url": url, "clickAction": url, "tag": f"{DOMAIN}_{game_id}"}},
                blocking=False,
            )
        except Exception:  # noqa: BLE001 - a failed push must never break the game
            _LOGGER.warning("Could not send notification via %s", service, exc_info=True)

    # --- exported state -------------------------------------------------

    def export(self) -> dict[str, Any]:
        """Return the state the frontend needs."""
        players = []
        for person in self.players:
            state = self.hass.states.get(person)
            s = self.stats(person)
            players.append({
                "person": person, "name": self.name(person),
                "user_id": state.attributes.get("user_id") if state else None,
                "picture": state.attributes.get("entity_picture") if state else None,
                **s, "played": s["wins"] + s["draws"] + s["losses"],
            })
        games = {
            gid: {**game, "active": self.active_player(game) if game.get("status") == STATUS_PLAYING else None}
            for gid, game in self.data["games"].items()
            if game["p1"] in self.players and game["p2"] in self.players
        }
        return {
            "players": players, "games": games, "total": self.data.get("total", 0), "last_result": self.data.get("last_result", ""),
            "points_win": self._opt(CONF_POINTS_WIN, DEFAULT_POINTS_WIN), "points_draw": self._opt(CONF_POINTS_DRAW, DEFAULT_POINTS_DRAW),
            "lightning_moves": self._opt(CONF_LIGHTNING_MOVES, DEFAULT_LIGHTNING_MOVES), "lightning_bonus": self._opt(CONF_LIGHTNING_BONUS, DEFAULT_LIGHTNING_BONUS),
        }
