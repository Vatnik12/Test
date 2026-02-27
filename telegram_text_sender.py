#!/usr/bin/env python3
"""Отправка текста из .txt файла в приватный Telegram-чат через бота."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import requests


def send_message(bot_token: str, chat_id: str, text: str, timeout: int = 15) -> dict:
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    response = requests.post(url, json=payload, timeout=timeout)
    response.raise_for_status()
    data = response.json()
    if not data.get("ok"):
        raise RuntimeError(f"Telegram API error: {data}")
    return data


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Отправка текста из файла в Telegram-чат")
    parser.add_argument("--file", required=True, help="Путь к .txt файлу")
    parser.add_argument("--chat-id", help="ID чата (если не задан, берется из TELEGRAM_CHAT_ID)")
    parser.add_argument("--bot-token", help="Токен бота (если не задан, берется из TELEGRAM_BOT_TOKEN)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    bot_token = args.bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = args.chat_id or os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token:
        raise SystemExit("Не указан bot token. Передайте --bot-token или TELEGRAM_BOT_TOKEN")
    if not chat_id:
        raise SystemExit("Не указан chat id. Передайте --chat-id или TELEGRAM_CHAT_ID")

    text = Path(args.file).read_text(encoding="utf-8").strip()
    if not text:
        raise SystemExit("Файл пустой: нечего отправлять")

    result = send_message(bot_token=bot_token, chat_id=chat_id, text=text)
    message_id = result["result"]["message_id"]
    print(f"Сообщение успешно отправлено. message_id={message_id}")


if __name__ == "__main__":
    main()
