"""Switch to turn push notifications on or off."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import FireParadConfigEntry
from .entity import FireParadEntity
from .manager import FireParadManager


async def async_setup_entry(hass: HomeAssistant, entry: FireParadConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    async_add_entities([FireParadNotifySwitch(entry.runtime_data)])


class FireParadNotifySwitch(FireParadEntity, SwitchEntity):
    """Push notifications when it is your turn."""

    _attr_translation_key = "notifications"
    _attr_icon = "mdi:cellphone-message"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, manager: FireParadManager) -> None:
        super().__init__(manager)
        self._attr_unique_id = f"{manager.entry.entry_id}_notifications"

    @property
    def is_on(self) -> bool:
        return self.manager.notify_enabled

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.manager.async_set_notify(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.manager.async_set_notify(False)
