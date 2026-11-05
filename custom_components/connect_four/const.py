"""Constants for Connect Four."""

from __future__ import annotations

from datetime import timedelta

DOMAIN = "connect_four"
# Earlier versions of this integration used this domain; its games and settings are imported once.
LEGACY_DOMAIN = "fire_pa_rad"
LEGACY_STATIC_URL = "/fire_pa_rad_static"
VERSION = "0.4.3"

# A waiting player may poke this long after the last move or poke.
POKE_INTERVAL = timedelta(minutes=30)

CONF_CONFIRM = "confirm"
CONF_PLAYERS = "players"
CONF_NOTIFY = "notify_services"
CONF_SHOW_PANEL = "show_panel"
# Users not linked to a player who may still play for everyone, e.g. a wall tablet.
CONF_SHARED_USERS = "shared_users"
CONF_POINTS_WIN = "points_win"
CONF_POINTS_DRAW = "points_draw"
CONF_LIGHTNING_MOVES = "lightning_moves"
CONF_LIGHTNING_BONUS = "lightning_bonus"

DEFAULT_POINTS_WIN = 3
DEFAULT_POINTS_DRAW = 1
DEFAULT_LIGHTNING_MOVES = 7
DEFAULT_LIGHTNING_BONUS = 1

NO_NOTIFY = "none"

STATIC_URL = "/connect_four_static"
FRONTEND_FILE = "connect-four.js"
PANEL_URL_PATH = "connect-four"
PANEL_ELEMENT = "connect-four-panel"

SUMMARY_ENTITY_ID = "sensor.connect_four"

STATUS_NONE = "none"
STATUS_PLAYING = "playing"
STATUS_FINISHED = "finished"

RESULT_DRAW = "draw"

SERVICE_START = "start"
SERVICE_DROP = "drop"
SERVICE_RESIGN = "resign"
SERVICE_RESET = "reset_scores"
SERVICE_SET_NOTIFICATIONS = "set_notifications"
SERVICE_POKE = "poke"

ATTR_GAME_ID = "game_id"
ATTR_COLUMN = "column"
ATTR_OPPONENT = "opponent"
ATTR_PLAYER = "player"
ATTR_ENABLED = "enabled"
