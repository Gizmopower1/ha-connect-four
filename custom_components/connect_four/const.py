"""Constants for Connect Four."""

from __future__ import annotations

DOMAIN = "connect_four"
# Earlier versions of this integration used this domain; its games and settings are imported once.
LEGACY_DOMAIN = "fire_pa_rad"
LEGACY_STATIC_URL = "/fire_pa_rad_static"
VERSION = "0.3.0"

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

ATTR_GAME_ID = "game_id"
ATTR_COLUMN = "column"
ATTR_OPPONENT = "opponent"
ATTR_PLAYER = "player"
ATTR_ENABLED = "enabled"
