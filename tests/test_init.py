"""Integration tests: config flow, services, rules and scoring."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from homeassistant import config_entries
from homeassistant.core import Context, HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.exceptions import ServiceValidationError

from custom_components.connect_four.const import CONF_NOTIFY, CONF_PLAYERS, DOMAIN, NO_NOTIFY

from pytest_homeassistant_custom_component.common import MockConfigEntry, async_mock_service

A, B, C = "person.player1", "person.player2", "person.player3"
GAME_AB = "player1__player2"


async def setup_entry(hass: HomeAssistant, notify: dict | None = None) -> MockConfigEntry:
    entry = MockConfigEntry(
        domain=DOMAIN, title="Connect Four", data={},
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
    return hass.states.get("sensor.connect_four").attributes


async def test_config_flow(hass, persons, frontend_mocks):
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    assert result["type"] is FlowResultType.FORM
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {CONF_PLAYERS: [A], "show_panel": True, "points_win": 3, "points_draw": 1, "lightning_moves": 7, "lightning_bonus": 1})
    assert result["errors"] == {"base": "min_players"}
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {CONF_PLAYERS: [A, B], "show_panel": True, "points_win": 3, "points_draw": 1, "lightning_moves": 7, "lightning_bonus": 1})
    assert result["step_id"] == "notify"
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {"Player1": NO_NOTIFY, "Player2": NO_NOTIFY})
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["options"][CONF_PLAYERS] == [A, B]
    assert result["options"][CONF_NOTIFY] == {A: NO_NOTIFY, B: NO_NOTIFY}
    await hass.async_block_till_done()
    assert hass.states.get("sensor.connect_four") is not None
    assert hass.states.get("sensor.connect_four_player1").state == "0"
    frontend_mocks["panel"].assert_called_once()


async def play(hass, game_id, columns, users):
    """Play columns, each by the user whose turn it is (users maps person -> user id)."""
    for col in columns:
        game = summary(hass)["games"][game_id]
        await call(hass, "drop", {"game_id": game_id, "column": col}, users[game["active"]])


async def test_full_game_scoring_and_rules(hass, persons, frontend_mocks):
    notify = async_mock_service(hass, "notify", "mobile_app_player2")
    await setup_entry(hass, notify={A: NO_NOTIFY, B: "notify.mobile_app_player2", C: NO_NOTIFY})
    users = {A: "user-player1", B: "user-player2", C: "user-player3"}

    with patch("custom_components.connect_four.manager.random.choice", return_value=1):
        response = await call(hass, "start", {"opponent": B}, "user-player1")
    assert response == {"game_id": GAME_AB}
    assert notify[-1].data["message"].startswith("Player1")
    assert hass.states.get("sensor.connect_four").state == "1"

    # Player2 may not move on Player1's turn, Player3 may not touch their game.
    with pytest.raises(ServiceValidationError):
        await call(hass, "drop", {"game_id": GAME_AB, "column": 0}, "user-player2")
    with pytest.raises(ServiceValidationError):
        await call(hass, "drop", {"game_id": GAME_AB, "column": 0}, "user-player3")

    # Player1 (R) stacks column 3, Player2 column 4 -> Player1 wins vertically in 4 moves (lightning bonus).
    await play(hass, GAME_AB, [3, 4, 3, 4, 3, 4, 3], users)
    game = summary(hass)["games"][GAME_AB]
    assert game["status"] == "finished"
    assert game["result"] == "1" and game["wins1"] == 1
    assert game["win"] == [17, 24, 31, 38]
    assert hass.states.get("sensor.connect_four_player1").state == "4"
    assert hass.states.get("sensor.connect_four_player2").attributes["losses"] == 1
    assert summary(hass)["total"] == 1

    # A shared tablet (no player user) may start for a pair and play; the series is kept.
    with patch("custom_components.connect_four.manager.random.choice", return_value=2):
        await call(hass, "start", {"player": A, "opponent": B}, "user-tablet")
    await call(hass, "drop", {"game_id": GAME_AB, "column": 0}, "user-tablet")
    await call(hass, "drop", {"game_id": GAME_AB, "column": 0}, None)
    # Player2 resigns from their phone, whether or not it is their turn.
    await call(hass, "resign", {"game_id": GAME_AB}, "user-player2")
    game = summary(hass)["games"][GAME_AB]
    assert game["status"] == "finished" and game["wins1"] == 2 and game["result"] == "1"
    assert hass.states.get("sensor.connect_four_player1").state == "7"


async def test_cancel_and_full_column(hass, persons, frontend_mocks):
    await setup_entry(hass)
    with patch("custom_components.connect_four.manager.random.choice", return_value=1):
        await call(hass, "start", {"opponent": C}, "user-player2")
    gid = "player2__player3"
    await call(hass, "resign", {"game_id": gid}, "user-player3")
    assert summary(hass)["games"][gid]["status"] == "none"
    assert summary(hass)["total"] == 0

    with patch("custom_components.connect_four.manager.random.choice", return_value=1):
        await call(hass, "start", {"opponent": C}, "user-player2")
    for _ in range(6):
        await call(hass, "drop", {"game_id": gid, "column": 0})
    with pytest.raises(ServiceValidationError):
        await call(hass, "drop", {"game_id": gid, "column": 0})


async def test_draw(hass, persons, frontend_mocks):
    await setup_entry(hass)
    with patch("custom_components.connect_four.manager.random.choice", return_value=1):
        await call(hass, "start", {"player": A, "opponent": C})
    gid = "player1__player3"
    # Column order that fills the board without four in a row.
    order = [0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0,
             2, 3, 2, 3, 2, 3, 3, 2, 3, 2, 3, 2,
             4, 5, 4, 5, 4, 5, 5, 4, 5, 4, 5, 4,
             6, 6, 6, 6, 6, 6]
    for col in order:
        await call(hass, "drop", {"game_id": gid, "column": col})
    game = summary(hass)["games"][gid]
    assert game["status"] == "finished" and game["result"] == "draw" and game["draws"] == 1
    assert hass.states.get("sensor.connect_four_player1").state == "1"
    assert hass.states.get("sensor.connect_four_player3").state == "1"


async def test_push_per_player_and_reset(hass, persons, frontend_mocks):
    notify = async_mock_service(hass, "notify", "mobile_app_player2")
    await setup_entry(hass, notify={A: NO_NOTIFY, B: "notify.mobile_app_player2", C: NO_NOTIFY})
    assert hass.states.get("switch.connect_four_push_player2").state == "on"

    # Player2 turns their own notifications off from the card.
    await call(hass, "set_notifications", {"enabled": False}, "user-player2")
    assert hass.states.get("switch.connect_four_push_player2").state == "off"
    assert next(p for p in summary(hass)["players"] if p["person"] == B)["push"] is False
    await call(hass, "start", {"opponent": B}, "user-player1")
    assert notify == []

    # Player1 may not change Player2's setting; the switch entity can.
    with pytest.raises(ServiceValidationError):
        await call(hass, "set_notifications", {"enabled": True, "player": B}, "user-player1")
    await hass.services.async_call("switch", "turn_on", {"entity_id": "switch.connect_four_push_player2"}, blocking=True)
    await call(hass, "resign", {"game_id": GAME_AB}, "user-player1")
    await call(hass, "start", {"opponent": B}, "user-player1")
    assert len(notify) == 1

    await hass.services.async_call(DOMAIN, "reset_scores", {}, blocking=True)
    assert summary(hass)["games"] == {}


async def test_imports_legacy_games_and_settings(hass, persons, frontend_mocks):
    """Games, scores and settings from the earlier fire_pa_rad integration carry over."""
    from homeassistant.helpers.storage import Store

    legacy = MockConfigEntry(domain="fire_pa_rad", options={CONF_PLAYERS: [A, B], CONF_NOTIFY: {A: NO_NOTIFY, B: NO_NOTIFY}})
    legacy.add_to_hass(hass)
    stats = {A: {"wins": 2, "draws": 0, "losses": 0, "points": 7}, B: {"wins": 0, "draws": 0, "losses": 2, "points": 0}}
    game = {"p1": A, "p2": B, "wins1": 2, "wins2": 0, "draws": 0, "status": "finished", "turn": 1, "board": "." * 42}
    await Store(hass, 1, f"fire_pa_rad.{legacy.entry_id}").async_save({"games": {GAME_AB: game}, "stats": stats, "total": 2, "last_result": "", "notify": True})

    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    schema = result["data_schema"].schema
    assert next(k for k in schema if k == CONF_PLAYERS).default() == [A, B]

    await setup_entry(hass)
    assert hass.states.get("sensor.connect_four_player1").state == "7"
    assert summary(hass)["games"][GAME_AB]["wins1"] == 2
    assert summary(hass)["total"] == 2
