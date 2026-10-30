"""Connect Four – a family game for Home Assistant."""

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
from homeassistant.helpers.start import async_at_started
from homeassistant.helpers.typing import ConfigType

from .const import (
    ATTR_COLUMN,
    ATTR_GAME_ID,
    ATTR_OPPONENT,
    ATTR_PLAYER,
    CONF_SHOW_PANEL,
    DOMAIN,
    FRONTEND_FILE,
    LEGACY_STATIC_URL,
    PANEL_ELEMENT,
    PANEL_URL_PATH,
    SERVICE_DROP,
    SERVICE_RESET,
    SERVICE_RESIGN,
    SERVICE_START,
    STATIC_URL,
    VERSION,
)
from .manager import ConnectFourManager

PLATFORMS = [Platform.SENSOR, Platform.SWITCH]
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

type ConnectFourConfigEntry = ConfigEntry[ConnectFourManager]

MODULE_URL = f"{STATIC_URL}/{FRONTEND_FILE}?v={VERSION}"


def _manager(hass: HomeAssistant) -> ConnectFourManager:
    entries = hass.config_entries.async_loaded_entries(DOMAIN)
    if not entries:
        raise ServiceValidationError(translation_domain=DOMAIN, translation_key="not_loaded")
    return entries[0].runtime_data


async def _async_register_lovelace_resource(hass: HomeAssistant) -> None:
    """Keep a dashboard resource for the card, so it is defined before any dashboard renders.

    Some layouts (e.g. layout-card) build their cards immediately and never retry,
    so relying only on add_extra_js_url can show a configuration error.
    """
    try:
        from homeassistant.components.lovelace.const import LOVELACE_DATA
        from homeassistant.components.lovelace.resources import ResourceStorageCollection
    except ImportError:
        return
    if (data := hass.data.get(LOVELACE_DATA)) is None or not isinstance(data.resources, ResourceStorageCollection):
        return
    resources = data.resources
    await resources.async_get_info()
    for item in resources.async_items():
        if str(item.get("url", "")).startswith(LEGACY_STATIC_URL):
            await resources.async_delete_item(item["id"])
    ours = [item for item in resources.async_items() if str(item.get("url", "")).startswith(STATIC_URL)]
    if not ours:
        await resources.async_create_item({"res_type": "module", "url": MODULE_URL})
        return
    if ours[0]["url"] != MODULE_URL:
        await resources.async_update_item(ours[0]["id"], {"res_type": "module", "url": MODULE_URL})
    for extra in ours[1:]:
        await resources.async_delete_item(extra["id"])


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Register the frontend file and the services."""
    await hass.http.async_register_static_paths(
        [StaticPathConfig(STATIC_URL, str(Path(__file__).parent / "frontend"), False)]
    )
    add_extra_js_url(hass, MODULE_URL)
    async_at_started(hass, _async_register_lovelace_resource)

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


async def async_setup_entry(hass: HomeAssistant, entry: ConnectFourConfigEntry) -> bool:
    """Set up Connect Four from a config entry."""
    manager = ConnectFourManager(hass, entry)
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


async def _async_reload(hass: HomeAssistant, entry: ConnectFourConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConnectFourConfigEntry) -> bool:
    """Unload a config entry."""
    async_remove_panel(hass, PANEL_URL_PATH, warn_if_unknown=False)
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
