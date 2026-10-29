"""Integration tests: config flow, services, rules and scoring."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from homeassistant import config_entries
from homeassistant.core import Context, HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.exceptions import ServiceValidationError

from custom_components.fire_pa_rad.const import CONF_NOTIFY, CONF_PLAYERS, DOMAIN, NO_NOTIFY

from pytest_homeassistant_custom_component.common import MockConfigEntry, async_mock_service

A, B, C = "person.anna", "person.bjorn", "person.cecilie"
GAME_AB = "anna__bjorn"


async def setup_entry(hass: HomeAssistant, notify: dict | None = None) -> MockConfigEntry:
    entry = MockConfigEntry(
        domain=DOMAIN, title="4 på rad", data={},
        options={CONF_PLAYERS: [A, B, C], CONF_NOTIFY: notify or {A: NO_NOTIFY, B: NO_NOTIFY, C: NO_NOTIFY}},
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


def ctx(user: str | None) -> Context:
    return Context(user_id=user)


async def call(hass, service, data, user=None):
    return await hass.services.async_call(DOMAIN, service, data, blocking=True, context=ctx(user), return_response=service == "start")


def summary(hass):
    return hass.states.get("sensor.fire_pa_rad").attributes


async def test_config_flow(hass, persons, frontend_mocks):
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    assert result["type"] is FlowResultType.FORM
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {CONF_PLAYERS: [A], "show_panel": True, "points_win": 3, "points_draw": 1, "lightning_moves": 7, "lightning_bonus": 1})
    assert result["errors"] == {"base": "min_players"}
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {CONF_PLAYERS: [A, B], "show_panel": True, "points_win": 3, "points_draw": 1, "lightning_moves": 7, "lightning_bonus": 1})
    assert result["step_id"] == "notify"
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {"Anna Test": NO_NOTIFY, "Bjørn Test": NO_NOTIFY})
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["options"][CONF_PLAYERS] == [A, B]
    assert result["options"][CONF_NOTIFY] == {A: NO_NOTIFY, B: NO_NOTIFY}
    await hass.async_block_till_done()
    assert hass.states.get("sensor.fire_pa_rad") is not None
    assert hass.states.get("sensor.fire_pa_rad_anna").state == "0"
    frontend_mocks["panel"].assert_called_once()


async def play(hass, game_id, columns, users):
    """Play columns, each by the user whose turn it is (users maps person -> user id)."""
    for col in columns:
        game = summary(hass)["games"][game_id]
        await call(hass, "drop", {"game_id": game_id, "column": col}, users[game["active"]])


async def test_full_game_scoring_and_rules(hass, persons, frontend_mocks):
    notify = async_mock_service(hass, "notify", "mobile_app_bjorn")
    await setup_entry(hass, notify={A: NO_NOTIFY, B: "notify.mobile_app_bjorn", C: NO_NOTIFY})
    users = {A: "user-anna", B: "user-bjorn", C: "user-cecilie"}

    with patch("custom_components.fire_pa_rad.manager.random.choice", return_value=1):
        response = await call(hass, "start", {"opponent": B}, "user-anna")
    assert response == {"game_id": GAME_AB}
    assert notify[-1].data["message"].startswith("Anna")
    assert hass.states.get("sensor.fire_pa_rad").state == "1"

    # Bjørn may not move on Anna's turn, Cecilie may not touch their game.
    with pytest.raises(ServiceValidationError):
        await call(hass, "drop", {"game_id": GAME_AB, "column": 0}, "user-bjorn")
    with pytest.raises(ServiceValidationError):
        await call(hass, "drop", {"game_id": GAME_AB, "column": 0}, "user-cecilie")

    # Anna (R) stacks column 3, Bjørn column 4 -> Anna wins vertically in 4 moves (lightning bonus).
    await play(hass, GAME_AB, [3, 4, 3, 4, 3, 4, 3], users)
    game = summary(hass)["games"][GAME_AB]
    assert game["status"] == "finished"
    assert game["result"] == "1" and game["wins1"] == 1
    assert game["win"] == [17, 24, 31, 38]
    assert hass.states.get("sensor.fire_pa_rad_anna").state == "4"
    assert hass.states.get("sensor.fire_pa_rad_bjorn").attributes["losses"] == 1
    assert summary(hass)["total"] == 1

    # A shared tablet (no player user) may start for a pair and play; the series is kept.
    with patch("custom_components.fire_pa_rad.manager.random.choice", return_value=2):
        await call(hass, "start", {"player": A, "opponent": B}, "user-tablet")
    await call(hass, "drop", {"game_id": GAME_AB, "column": 0}, "user-tablet")
    await call(hass, "drop", {"game_id": GAME_AB, "column": 0}, None)
    # Bjørn resigns from his phone even though it is his turn or not.
    await call(hass, "resign", {"game_id": GAME_AB}, "user-bjorn")
    game = summary(hass)["games"][GAME_AB]
    assert game["status"] == "finished" and game["wins1"] == 2 and game["result"] == "1"
    assert hass.states.get("sensor.fire_pa_rad_anna").state == "7"


async def test_cancel_and_full_column(hass, persons, frontend_mocks):
    await setup_entry(hass)
    with patch("custom_components.fire_pa_rad.manager.random.choice", return_value=1):
        await call(hass, "start", {"opponent": C}, "user-bjorn")
    gid = "bjorn__cecilie"
    await call(hass, "resign", {"game_id": gid}, "user-cecilie")
    assert summary(hass)["games"][gid]["status"] == "none"
    assert summary(hass)["total"] == 0

    with patch("custom_components.fire_pa_rad.manager.random.choice", return_value=1):
        await call(hass, "start", {"opponent": C}, "user-bjorn")
    for _ in range(6):
        await call(hass, "drop", {"game_id": gid, "column": 0})
    with pytest.raises(ServiceValidationError):
        await call(hass, "drop", {"game_id": gid, "column": 0})


async def test_draw(hass, persons, frontend_mocks):
    await setup_entry(hass)
    with patch("custom_components.fire_pa_rad.manager.random.choice", return_value=1):
        await call(hass, "start", {"player": A, "opponent": C})
    gid = "anna__cecilie"
    # Column order that fills the board without four in a row.
    order = [0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0,
             2, 3, 2, 3, 2, 3, 3, 2, 3, 2, 3, 2,
             4, 5, 4, 5, 4, 5, 5, 4, 5, 4, 5, 4,
             6, 6, 6, 6, 6, 6]
    for col in order:
        await call(hass, "drop", {"game_id": gid, "column": col})
    game = summary(hass)["games"][gid]
    assert game["status"] == "finished" and game["result"] == "draw" and game["draws"] == 1
    assert hass.states.get("sensor.fire_pa_rad_anna").state == "1"
    assert hass.states.get("sensor.fire_pa_rad_cecilie").state == "1"


async def test_notifications_switch_and_reset(hass, persons, frontend_mocks):
    notify = async_mock_service(hass, "notify", "mobile_app_bjorn")
    await setup_entry(hass, notify={A: NO_NOTIFY, B: "notify.mobile_app_bjorn", C: NO_NOTIFY})
    switch = next(s.entity_id for s in hass.states.async_all("switch"))
    await hass.services.async_call("switch", "turn_off", {"entity_id": switch}, blocking=True)
    await call(hass, "start", {"opponent": B}, "user-anna")
    assert notify == []
    await hass.services.async_call(DOMAIN, "reset_scores", {}, blocking=True)
    assert summary(hass)["games"] == {}
