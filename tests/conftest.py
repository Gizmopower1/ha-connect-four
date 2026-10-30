"""Fixtures for Connect Four tests."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from homeassistant.core import HomeAssistant

PERSONS = {
    "person.player1": ("Player1", "user-player1"),
    "person.player2": ("Player2", "user-player2"),
    "person.player3": ("Player3", "user-player3"),
}


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Allow loading custom_components in every test."""
    return


@pytest.fixture
def frontend_mocks():
    """Avoid needing the real frontend/http stack."""
    with (
        patch("custom_components.connect_four.add_extra_js_url") as js,
        patch("custom_components.connect_four.async_register_built_in_panel") as panel,
        patch("custom_components.connect_four.async_remove_panel") as remove,
    ):
        yield {"js": js, "panel": panel, "remove": remove}


@pytest.fixture
async def persons(hass: HomeAssistant):
    """Create person states linked to users, and fake the dependencies."""
    hass.config.components.update({"frontend", "http", "person"})
    hass.http = MagicMock()
    hass.http.async_register_static_paths = AsyncMock()
    for entity_id, (name, user_id) in PERSONS.items():
        hass.states.async_set(entity_id, "home", {"friendly_name": name, "user_id": user_id, "device_trackers": []})
    return PERSONS
