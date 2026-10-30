"""Sensors: one summary sensor (used by the card) and points per player."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import ConnectFourConfigEntry
from .const import STATUS_PLAYING, SUMMARY_ENTITY_ID
from .entity import ConnectFourEntity
from .manager import ConnectFourManager


async def async_setup_entry(hass: HomeAssistant, entry: ConnectFourConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    manager = entry.runtime_data
    entities: list[SensorEntity] = [ConnectFourSummarySensor(manager)]
    entities += [ConnectFourPointsSensor(manager, person) for person in manager.players]
    async_add_entities(entities)


class ConnectFourSummarySensor(ConnectFourEntity, SensorEntity):
    """Number of games in progress; attributes carry everything the card needs."""

    _attr_translation_key = "games"
    _attr_icon = "mdi:circle-multiple"
    _unrecorded_attributes = frozenset({"games", "players", "last_result"})

    def __init__(self, manager: ConnectFourManager) -> None:
        super().__init__(manager)
        self._attr_unique_id = f"{manager.entry.entry_id}_games"
        self.entity_id = SUMMARY_ENTITY_ID

    @property
    def native_value(self) -> int:
        return sum(1 for game in self.manager.data["games"].values() if game.get("status") == STATUS_PLAYING)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return self.manager.export()


class ConnectFourPointsSensor(ConnectFourEntity, SensorEntity):
    """Total points for one player."""

    _attr_translation_key = "points"
    _attr_icon = "mdi:star-circle"
    _attr_state_class = SensorStateClass.TOTAL

    def __init__(self, manager: ConnectFourManager, person: str) -> None:
        super().__init__(manager)
        self.person = person
        slug = person.split(".", 1)[1]
        self._attr_unique_id = f"{manager.entry.entry_id}_points_{slug}"
        self._attr_translation_placeholders = {"name": manager.name(person)}
        self.entity_id = f"sensor.connect_four_{slug}"

    @property
    def native_value(self) -> int:
        return self.manager.stats(self.person)["points"]

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        s = self.manager.stats(self.person)
        return {"person": self.person, **s, "played": s["wins"] + s["draws"] + s["losses"]}
