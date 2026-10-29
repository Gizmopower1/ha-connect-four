"""Sensors: one summary sensor (used by the card) and points per player."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import FireParadConfigEntry
from .const import STATUS_PLAYING, SUMMARY_ENTITY_ID
from .entity import FireParadEntity
from .manager import FireParadManager


async def async_setup_entry(hass: HomeAssistant, entry: FireParadConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    manager = entry.runtime_data
    entities: list[SensorEntity] = [FireParadSummarySensor(manager)]
    entities += [FireParadPointsSensor(manager, person) for person in manager.players]
    async_add_entities(entities)


class FireParadSummarySensor(FireParadEntity, SensorEntity):
    """Number of games in progress; attributes carry everything the card needs."""

    _attr_translation_key = "games"
    _attr_icon = "mdi:circle-multiple"
    _unrecorded_attributes = frozenset({"games", "players", "last_result"})

    def __init__(self, manager: FireParadManager) -> None:
        super().__init__(manager)
        self._attr_unique_id = f"{manager.entry.entry_id}_games"
        self.entity_id = SUMMARY_ENTITY_ID

    @property
    def native_value(self) -> int:
        return sum(1 for game in self.manager.data["games"].values() if game.get("status") == STATUS_PLAYING)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return self.manager.export()


class FireParadPointsSensor(FireParadEntity, SensorEntity):
    """Total points for one player."""

    _attr_translation_key = "points"
    _attr_icon = "mdi:star-circle"
    _attr_state_class = SensorStateClass.TOTAL

    def __init__(self, manager: FireParadManager, person: str) -> None:
        super().__init__(manager)
        self.person = person
        slug = person.split(".", 1)[1]
        self._attr_unique_id = f"{manager.entry.entry_id}_points_{slug}"
        self._attr_translation_placeholders = {"name": manager.name(person)}
        self.entity_id = f"sensor.fire_pa_rad_{slug}"

    @property
    def native_value(self) -> int:
        return self.manager.stats(self.person)["points"]

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        s = self.manager.stats(self.person)
        return {"person": self.person, **s, "played": s["wins"] + s["draws"] + s["losses"]}
