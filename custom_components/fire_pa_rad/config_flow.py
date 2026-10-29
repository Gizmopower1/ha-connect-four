"""Config and options flow: pick the players and their phones."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr, entity_registry as er, selector
from homeassistant.util import slugify

from .const import (
    CONF_LIGHTNING_BONUS,
    CONF_LIGHTNING_MOVES,
    CONF_NOTIFY,
    CONF_PLAYERS,
    CONF_POINTS_DRAW,
    CONF_POINTS_WIN,
    CONF_SHOW_PANEL,
    DEFAULT_LIGHTNING_BONUS,
    DEFAULT_LIGHTNING_MOVES,
    DEFAULT_POINTS_DRAW,
    DEFAULT_POINTS_WIN,
    DOMAIN,
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


def _label(hass: HomeAssistant, person: str) -> str:
    state = hass.states.get(person)
    return state.name if state else person


def _players_schema(hass: HomeAssistant, current: dict[str, Any]) -> vol.Schema:
    default_players = current.get(CONF_PLAYERS) or [s.entity_id for s in hass.states.async_all("person")]
    return vol.Schema({
        vol.Required(CONF_PLAYERS, default=default_players): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="person", multiple=True)
        ),
        vol.Required(CONF_SHOW_PANEL, default=current.get(CONF_SHOW_PANEL, True)): selector.BooleanSelector(),
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


def _collect_notify(hass: HomeAssistant, players: list[str], user_input: dict[str, Any]) -> dict[str, str]:
    return {p: user_input.get(_label(hass, p), NO_NOTIFY) for p in players}


class FireParadConfigFlow(ConfigFlow, domain=DOMAIN):
    """Set up 4 på rad."""

    VERSION = 1

    def __init__(self) -> None:
        self._options: dict[str, Any] = {}

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            if len(user_input[CONF_PLAYERS]) < 2:
                errors["base"] = "min_players"
            else:
                self._options = {k: (int(v) if isinstance(v, float) else v) for k, v in user_input.items()}
                return await self.async_step_notify()
        return self.async_show_form(step_id="user", data_schema=_players_schema(self.hass, user_input or {}), errors=errors)

    async def async_step_notify(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        players = self._options[CONF_PLAYERS]
        if user_input is not None:
            self._options[CONF_NOTIFY] = _collect_notify(self.hass, players, user_input)
            title = "4 på rad" if (self.hass.config.language or "").split("-")[0] in ("nb", "no", "nn") else "Connect Four"
            return self.async_create_entry(title=title, data={}, options=self._options)
        return self.async_show_form(step_id="notify", data_schema=_notify_schema(self.hass, players, {}))

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> FireParadOptionsFlow:
        return FireParadOptionsFlow()


class FireParadOptionsFlow(OptionsFlow):
    """Change players, phones and scoring."""

    def __init__(self) -> None:
        self._options: dict[str, Any] = {}

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            if len(user_input[CONF_PLAYERS]) < 2:
                errors["base"] = "min_players"
            else:
                self._options = {**self.config_entry.options, **{k: (int(v) if isinstance(v, float) else v) for k, v in user_input.items()}}
                return await self.async_step_notify()
        return self.async_show_form(step_id="init", data_schema=_players_schema(self.hass, dict(self.config_entry.options)), errors=errors)

    async def async_step_notify(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        players = self._options[CONF_PLAYERS]
        if user_input is not None:
            self._options[CONF_NOTIFY] = _collect_notify(self.hass, players, user_input)
            return self.async_create_entry(data=self._options)
        return self.async_show_form(
            step_id="notify", data_schema=_notify_schema(self.hass, players, self.config_entry.options.get(CONF_NOTIFY, {}))
        )
