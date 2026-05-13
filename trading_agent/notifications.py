from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import Any
import urllib.request
import urllib.error


class NotificationAdapter(ABC):
    @abstractmethod
    def send(self, message: str) -> bool:
        """Send notification message. Returns True if successful."""
        raise NotImplementedError


class TelegramAdapter(NotificationAdapter):
    def __init__(self, token: str | None = None, chat_id: str | None = None):
        self.token = token or os.environ.get("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.environ.get("TELEGRAM_CHAT_ID")

    def send(self, message: str) -> bool:
        if not self.token or not self.chat_id:
            return False
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        data = {"chat_id": self.chat_id, "text": message, "parse_mode": "HTML"}
        try:
            req = urllib.request.Request(
                url,
                data=urllib.parse.urlencode(data).encode("utf-8"),
                method="POST",
            )
            urllib.request.urlopen(req, timeout=10)
            return True
        except urllib.error.URLError:
            return False


class WhatsAppAdapter(NotificationAdapter):
    """WhatsApp via Ultramsg.com or similar REST API."""

    def __init__(self, instance_id: str | None = None, token: str | None = None, to: str | None = None):
        self.instance_id = instance_id or os.environ.get("WHATSAPP_INSTANCE_ID")
        self.token = token or os.environ.get("WHATSAPP_TOKEN")
        self.to = to or os.environ.get("WHATSAPP_TO")

    def send(self, message: str) -> bool:
        if not self.instance_id or not self.token or not self.to:
            return False
        url = f"https://api.ultramsg.com/{self.instance_id}/messages/chat"
        data = {
            "token": self.token,
            "to": self.to,
            "body": message,
        }
        try:
            req = urllib.request.Request(
                url,
                data=urllib.parse.urlencode(data).encode("utf-8"),
                method="POST",
            )
            urllib.request.urlopen(req, timeout=10)
            return True
        except urllib.error.URLError:
            return False


class NotificationService:
    def __init__(self, adapters: list[NotificationAdapter] | None = None):
        self.adapters = adapters or []

    def notify(self, message: str) -> None:
        """Send to all configured adapters."""
        for adapter in self.adapters:
            try:
                adapter.send(message)
            except Exception:
                pass


def create_notification_service() -> NotificationService:
    """Create notification service from environment or config."""
    adapters: list[NotificationAdapter] = []

    if os.environ.get("TELEGRAM_BOT_TOKEN") and os.environ.get("TELEGRAM_CHAT_ID"):
        adapters.append(TelegramAdapter())

    if os.environ.get("WHATSAPP_INSTANCE_ID") and os.environ.get("WHATSAPP_TOKEN") and os.environ.get("WHATSAPP_TO"):
        adapters.append(WhatsAppAdapter())

    return NotificationService(adapters)