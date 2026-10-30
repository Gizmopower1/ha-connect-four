"""Switches to turn push notifications on or off for each player."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import ConnectFourConfigEntry
from .const import DOMAIN
from .entity import ConnectFourEntity
from .manager import ConnectFourManager


async def async_setup_entry(hass: HomeAssistant, entry: ConnectFourConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    # Version 0.2 had one switch for everyone; it is replaced by one switch per player.
    ent_reg = er.async_get(hass)
    if old := ent_reg.async_get_entity_id("switch", DOMAIN, f"{entry.entry_id}_notifications"):
        ent_reg.async_remove(old)
    manager = entry.runtime_data
    async_add_entities([ConnectFourPushSwitch(manager, person) for person in manager.players])


class ConnectFourPushSwitch(ConnectFourEntity, SwitchEntity):
    """Push notifications for one player when it is their turn."""

    _attr_translation_key = "push"
    _attr_icon = "mdi:cellphone-message"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, manager: ConnectFourManager, person: str) -> None:
        super().__init__(manager)
        self.person = person
        slug = person.split(".", 1)[1]
        self._attr_unique_id = f"{manager.entry.entry_id}_push_{slug}"
        self._attr_translation_placeholders = {"name": manager.name(person)}
        self.entity_id = f"switch.connect_four_push_{slug}"

    @property
    def is_on(self) -> bool:
        return self.manager.push_enabled(self.person)

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.manager.async_set_push(self.person, True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.manager.async_set_push(self.person, False)
