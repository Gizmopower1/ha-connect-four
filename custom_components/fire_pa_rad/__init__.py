"""4 på rad – a Connect Four game for the whole family in Home Assistant."""

from __future__ import annotations

from pathlib import Path

import voluptuous as vol

from homeassistant.components.frontend import add_extra_js_url, async_register_built_in_panel, async_remove_panel
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.service import async_register_admin_service
from homeassistant.helpers.typing import ConfigType

from .const import (
    ATTR_COLUMN,
    ATTR_GAME_ID,
    ATTR_OPPONENT,
    ATTR_PLAYER,
    CONF_SHOW_PANEL,
    DOMAIN,
    FRONTEND_FILE,
    PANEL_ELEMENT,
    PANEL_URL_PATH,
    SERVICE_DROP,
    SERVICE_RESET,
    SERVICE_RESIGN,
    SERVICE_START,
    STATIC_URL,
    VERSION,
)
from .manager import FireParadManager

PLATFORMS = [Platform.SENSOR, Platform.SWITCH]
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

type FireParadConfigEntry = ConfigEntry[FireParadManager]

MODULE_URL = f"{STATIC_URL}/{FRONTEND_FILE}?v={VERSION}"


def _manager(hass: HomeAssistant) -> FireParadManager:
    entries = hass.config_entries.async_loaded_entries(DOMAIN)
    if not entries:
        raise ServiceValidationError(translation_domain=DOMAIN, translation_key="not_loaded")
    return entries[0].runtime_data


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Register the frontend file and the services."""
    await hass.http.async_register_static_paths(
        [StaticPathConfig(STATIC_URL, str(Path(__file__).parent / "frontend"), False)]
    )
    add_extra_js_url(hass, MODULE_URL)

    async def start(call: ServiceCall) -> ServiceResponse:
        game_id = await _manager(hass).async_start(call.context.user_id, call.data[ATTR_OPPONENT], call.data.get(ATTR_PLAYER))
        return {"game_id": game_id}

    async def drop(call: ServiceCall) -> None:
        await _manager(hass).async_drop(call.context.user_id, call.data[ATTR_GAME_ID], call.data[ATTR_COLUMN])

    async def resign(call: ServiceCall) -> None:
        await _manager(hass).async_resign(call.context.user_id, call.data[ATTR_GAME_ID])

    async def reset(call: ServiceCall) -> None:
        await _manager(hass).async_reset()

    hass.services.async_register(
        DOMAIN, SERVICE_START, start,
        schema=vol.Schema({vol.Required(ATTR_OPPONENT): cv.entity_id, vol.Optional(ATTR_PLAYER): cv.entity_id}),
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        DOMAIN, SERVICE_DROP, drop,
        schema=vol.Schema({vol.Required(ATTR_GAME_ID): cv.string, vol.Required(ATTR_COLUMN): vol.All(vol.Coerce(int), vol.Range(min=0, max=6))}),
    )
    hass.services.async_register(DOMAIN, SERVICE_RESIGN, resign, schema=vol.Schema({vol.Required(ATTR_GAME_ID): cv.string}))
    async_register_admin_service(hass, DOMAIN, SERVICE_RESET, reset)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: FireParadConfigEntry) -> bool:
    """Set up 4 på rad from a config entry."""
    manager = FireParadManager(hass, entry)
    await manager.async_load()
    entry.runtime_data = manager

    if entry.options.get(CONF_SHOW_PANEL, True):
        async_register_built_in_panel(
            hass,
            component_name="custom",
            sidebar_title=entry.title,
            sidebar_icon="mdi:circle-multiple",
            frontend_url_path=PANEL_URL_PATH,
            config={"_panel_custom": {"name": PANEL_ELEMENT, "module_url": MODULE_URL, "embed_iframe": False, "trust_external": False}},
            require_admin=False,
            update=True,
        )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_reload))
    return True


async def _async_reload(hass: HomeAssistant, entry: FireParadConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: FireParadConfigEntry) -> bool:
    """Unload a config entry."""
    async_remove_panel(hass, PANEL_URL_PATH, warn_if_unknown=False)
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
