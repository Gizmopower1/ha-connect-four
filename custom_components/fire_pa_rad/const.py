"""Constants for 4 på rad."""

from __future__ import annotations

DOMAIN = "fire_pa_rad"
VERSION = "0.1.1"

CONF_PLAYERS = "players"
CONF_NOTIFY = "notify_services"
CONF_SHOW_PANEL = "show_panel"
CONF_POINTS_WIN = "points_win"
CONF_POINTS_DRAW = "points_draw"
CONF_LIGHTNING_MOVES = "lightning_moves"
CONF_LIGHTNING_BONUS = "lightning_bonus"

DEFAULT_POINTS_WIN = 3
DEFAULT_POINTS_DRAW = 1
DEFAULT_LIGHTNING_MOVES = 7
DEFAULT_LIGHTNING_BONUS = 1

NO_NOTIFY = "none"

STATIC_URL = "/fire_pa_rad_static"
FRONTEND_FILE = "fire-pa-rad.js"
PANEL_URL_PATH = "fire-pa-rad"
PANEL_ELEMENT = "fire-pa-rad-panel"

SUMMARY_ENTITY_ID = "sensor.fire_pa_rad"

STATUS_NONE = "none"
STATUS_PLAYING = "playing"
STATUS_FINISHED = "finished"

RESULT_DRAW = "draw"

SERVICE_START = "start"
SERVICE_DROP = "drop"
SERVICE_RESIGN = "resign"
SERVICE_RESET = "reset_scores"

ATTR_GAME_ID = "game_id"
ATTR_COLUMN = "column"
ATTR_OPPONENT = "opponent"
ATTR_PLAYER = "player"
