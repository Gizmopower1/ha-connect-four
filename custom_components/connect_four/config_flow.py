"""Config and options flow: pick the players and their phones."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigEntryState, ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr, entity_registry as er, selector
from homeassistant.util import slugify

from .const import (
    CONF_CONFIRM,
    CONF_LIGHTNING_BONUS,
    CONF_LIGHTNING_MOVES,
    CONF_NOTIFY,
    CONF_EXIT_LABEL,
    CONF_EXIT_PATH,
    CONF_NOTIFY_PATH,
    CONF_PLAYERS,
    CONF_POINTS_DRAW,
    CONF_POINTS_WIN,
    CONF_SHARED_USERS,
    CONF_SHOW_PANEL,
    DEFAULT_LIGHTNING_BONUS,
    DEFAULT_LIGHTNING_MOVES,
    DEFAULT_POINTS_DRAW,
    DEFAULT_POINTS_WIN,
    DOMAIN,
    LEGACY_DOMAIN,
    NO_NOTIFY,
)


def _notify_services(hass: HomeAssistant) -> list[str]:
    services = hass.services.async_services().get("notify", {})
    return sorted(f"notify.{name}" for name in services if name.startswith("mobile_app_"))


def _guess_notify(hass: HomeAssistant, person: str) -> str:
    """Find the mobile app notify service of a person's phone via its device trackers."""
    state = hass.states.get(person)
    if state is None:
        return NO_NOTIFY
    ent_reg, dev_reg = er.async_get(hass), dr.async_get(hass)
    for tracker in state.attributes.get("device_trackers", []):
        entry = ent_reg.async_get(tracker)
        if entry and entry.platform == "mobile_app" and entry.device_id and (device := dev_reg.async_get(entry.device_id)):
            service = f"mobile_app_{slugify(device.name or '')}"
            if hass.services.has_service("notify", service):
                return f"notify.{service}"
    return NO_NOTIFY


def _legacy_options(hass: HomeAssistant) -> dict[str, Any]:
    """Settings from the earlier fire_pa_rad integration, used as defaults."""
    entries = hass.config_entries.async_entries(LEGACY_DOMAIN)
    return dict(entries[0].options) if entries else {}


def _label(hass: HomeAssistant, person: str) -> str:
    state = hass.states.get(person)
    return state.name if state else person


async def _user_options(hass: HomeAssistant) -> list[selector.SelectOptionDict]:
    """Active, human Home Assistant users, for picking shared users such as a wall tablet."""
    users = [u for u in await hass.auth.async_get_users() if u.is_active and not u.system_generated]
    return [selector.SelectOptionDict(value=u.id, label=u.name or u.id) for u in sorted(users, key=lambda u: (u.name or "").lower())]


async def _players_schema(hass: HomeAssistant, current: dict[str, Any]) -> vol.Schema:
    default_players = current.get(CONF_PLAYERS) or [s.entity_id for s in hass.states.async_all("person")]
    users = await _user_options(hass)
    known = {u["value"] for u in users}
    default_shared = [u for u in current.get(CONF_SHARED_USERS, []) if u in known]
    return vol.Schema({
        vol.Required(CONF_PLAYERS, default=default_players): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="person", multiple=True)
        ),
        vol.Optional(CONF_SHARED_USERS, default=default_shared): selector.SelectSelector(
            selector.SelectSelectorConfig(options=users, multiple=True, mode=selector.SelectSelectorMode.DROPDOWN)
        ),
        vol.Required(CONF_SHOW_PANEL, default=current.get(CONF_SHOW_PANEL, True)): selector.BooleanSelector(),
        vol.Optional(CONF_NOTIFY_PATH, default=current.get(CONF_NOTIFY_PATH, "")): selector.TextSelector(),
        vol.Optional(CONF_EXIT_PATH, default=current.get(CONF_EXIT_PATH, "")): selector.TextSelector(),
        vol.Optional(CONF_EXIT_LABEL, default=current.get(CONF_EXIT_LABEL, "")): selector.TextSelector(),
        vol.Required(CONF_POINTS_WIN, default=current.get(CONF_POINTS_WIN, DEFAULT_POINTS_WIN)): selector.NumberSelector(
            selector.NumberSelectorConfig(min=0, max=10, mode=selector.NumberSelectorMode.BOX)
        ),
        vol.Required(CONF_POINTS_DRAW, default=current.get(CONF_POINTS_DRAW, DEFAULT_POINTS_DRAW)): selector.NumberSelector(
            selector.NumberSelectorConfig(min=0, max=10, mode=selector.NumberSelectorMode.BOX)
        ),
        vol.Required(CONF_LIGHTNING_MOVES, default=current.get(CONF_LIGHTNING_MOVES, DEFAULT_LIGHTNING_MOVES)): selector.NumberSelector(
            selector.NumberSelectorConfig(min=0, max=21, mode=selector.NumberSelectorMode.BOX)
        ),
        vol.Required(CONF_LIGHTNING_BONUS, default=current.get(CONF_LIGHTNING_BONUS, DEFAULT_LIGHTNING_BONUS)): selector.NumberSelector(
            selector.NumberSelectorConfig(min=0, max=10, mode=selector.NumberSelectorMode.BOX)
        ),
    })


def _notify_schema(hass: HomeAssistant, players: list[str], current: dict[str, str]) -> vol.Schema:
    options = [selector.SelectOptionDict(value=NO_NOTIFY, label="—")] + [
        selector.SelectOptionDict(value=s, label=s) for s in _notify_services(hass)
    ]
    return vol.Schema({
        vol.Required(_label(hass, p), default=current.get(p) or _guess_notify(hass, p)): selector.SelectSelector(
            selector.SelectSelectorConfig(options=options, mode=selector.SelectSelectorMode.DROPDOWN)
        )
        for p in players
    })


def _check_settings(user_input: dict[str, Any]) -> dict[str, str]:
    if len(user_input[CONF_PLAYERS]) < 2:
        return {"base": "min_players"}
    for key in (CONF_NOTIFY_PATH, CONF_EXIT_PATH):
        path = (user_input.get(key) or "").strip()
        if path and (not path.startswith("/") or path.startswith("//") or " " in path):
            return {key: "invalid_path"}
    return {}


def _clean(user_input: dict[str, Any]) -> dict[str, Any]:
    options = {k: (int(v) if isinstance(v, float) else v) for k, v in user_input.items()}
    for key in (CONF_NOTIFY_PATH, CONF_EXIT_PATH, CONF_EXIT_LABEL):
        options[key] = (options.get(key) or "").strip()
    return options


def _collect_notify(hass: HomeAssistant, players: list[str], user_input: dict[str, Any]) -> dict[str, str]:
    return {p: user_input.get(_label(hass, p), NO_NOTIFY) for p in players}


class ConnectFourConfigFlow(ConfigFlow, domain=DOMAIN):
    """Set up Connect Four."""

    VERSION = 1

    def __init__(self) -> None:
        self._options: dict[str, Any] = {}

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            if not (errors := _check_settings(user_input)):
                self._options = _clean(user_input)
                return await self.async_step_notify()
        return self.async_show_form(step_id="user", data_schema=await _players_schema(self.hass, user_input or _legacy_options(self.hass)), errors=errors)

    async def async_step_notify(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        players = self._options[CONF_PLAYERS]
        if user_input is not None:
            self._options[CONF_NOTIFY] = _collect_notify(self.hass, players, user_input)
            return self.async_create_entry(title="Connect Four", data={}, options=self._options)
        legacy = _legacy_options(self.hass).get(CONF_NOTIFY, {})
        return self.async_show_form(step_id="notify", data_schema=_notify_schema(self.hass, players, legacy))

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> ConnectFourOptionsFlow:
        return ConnectFourOptionsFlow()


class ConnectFourOptionsFlow(OptionsFlow):
    """Change players, phones and scoring, or reset the games and points."""

    def __init__(self) -> None:
        self._options: dict[str, Any] = {}

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        return self.async_show_menu(step_id="init", menu_options=["settings", "reset"])

    async def async_step_reset(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Remove all games, series and points after an explicit confirmation."""
        if self.config_entry.state is not ConfigEntryState.LOADED:
            return self.async_abort(reason="not_loaded")
        errors: dict[str, str] = {}
        if user_input is not None:
            if user_input[CONF_CONFIRM]:
                await self.config_entry.runtime_data.async_reset()
                return self.async_abort(reason="reset_done")
            errors["base"] = "confirm_required"
        return self.async_show_form(
            step_id="reset",
            data_schema=vol.Schema({vol.Required(CONF_CONFIRM, default=False): selector.BooleanSelector()}),
            errors=errors,
        )

    async def async_step_settings(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            if not (errors := _check_settings(user_input)):
                self._options = {**self.config_entry.options, **_clean(user_input)}
                return await self.async_step_notify()
        return self.async_show_form(step_id="settings", data_schema=await _players_schema(self.hass, dict(self.config_entry.options)), errors=errors)

    async def async_step_notify(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        players = self._options[CONF_PLAYERS]
        if user_input is not None:
            self._options[CONF_NOTIFY] = _collect_notify(self.hass, players, user_input)
            return self.async_create_entry(data=self._options)
        return self.async_show_form(
            step_id="notify", data_schema=_notify_schema(self.hass, players, self.config_entry.options.get(CONF_NOTIFY, {}))
        )
