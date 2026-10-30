"""The integration keeps exactly one up-to-date dashboard resource for its card."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

from homeassistant.components.lovelace.const import LOVELACE_DATA
from homeassistant.components.lovelace.resources import ResourceStorageCollection

from custom_components.connect_four import MODULE_URL, _async_register_lovelace_resource


async def test_creates_updates_and_dedupes_resource(hass):
    ll_config = MagicMock()
    ll_config.async_load = AsyncMock(return_value={})
    resources = ResourceStorageCollection(hass, ll_config)
    hass.data[LOVELACE_DATA] = SimpleNamespace(resources=resources)

    await _async_register_lovelace_resource(hass)
    assert [r["url"] for r in resources.async_items()] == [MODULE_URL]

    # An old version, a duplicate and the legacy fire_pa_rad resource are reduced to one current entry.
    item = resources.async_items()[0]
    await resources.async_update_item(item["id"], {"res_type": "module", "url": "/connect_four_static/connect-four.js?v=0.0.1"})
    await resources.async_create_item({"res_type": "module", "url": "/connect_four_static/connect-four.js?v=0.0.2"})
    await resources.async_create_item({"res_type": "module", "url": "/hacsfiles/other/card.js"})
    await resources.async_create_item({"res_type": "module", "url": "/fire_pa_rad_static/fire-pa-rad.js?v=0.1.1"})
    await _async_register_lovelace_resource(hass)
    urls = sorted(r["url"] for r in resources.async_items())
    assert urls == sorted([MODULE_URL, "/hacsfiles/other/card.js"])


async def test_no_lovelace_is_fine(hass):
    hass.data.pop(LOVELACE_DATA, None)
    await _async_register_lovelace_resource(hass)
