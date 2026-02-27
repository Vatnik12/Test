# Тестовое задание: Email + Telegram + Архитектура

Этот репозиторий содержит все части задания в одном месте:
- скрипт проверки email-доменов и SMTP-handshake;
- скрипт отправки текста в Telegram-чат через бота;
- архитектурное решение для 1200 email-адресов;
- блиц по AI-стеку.

## Содержимое
- `email_domain_checker.py` — задача №1.
- `telegram_text_sender.py` — задача №2.
- `ARCHITECTURE.md` — задача №3.
- `BLITZ_AI_STACK.md` — задача №4.

## Требования
- Python 3.10+
- Пакеты:
  - `dnspython`
  - `requests`

Установка:
```bash
python -m venv .venv
source .venv/bin/activate
pip install dnspython requests
```

## 1) Проверка email-доменов
Скрипт:
- принимает email-адреса через аргументы и/или из txt-файла;
- проверяет MX-записи домена;
- делает SMTP handshake (MAIL FROM + RCPT TO, без отправки письма);
- выводит статус:
  - `домен валиден`;
  - `домен отсутствует`;
  - `MX-записи отсутствуют или некорректны`.

Пример запуска:
```bash
python email_domain_checker.py user1@gmail.com invalid@nonexistent-domain-12345.com
python email_domain_checker.py --file emails.txt
```

## 2) Мини-интеграция с Telegram
Скрипт:
- читает текст из `.txt`;
- отправляет его в приватный чат через Telegram-бота.

Вариант через переменные окружения:
```bash
export TELEGRAM_BOT_TOKEN="<TOKEN>"
export TELEGRAM_CHAT_ID="<CHAT_ID>"
python telegram_text_sender.py --file message.txt
```

Вариант через аргументы:
```bash
python telegram_text_sender.py --file message.txt --bot-token "<TOKEN>" --chat-id "<CHAT_ID>"
```

## Примечания
- Некоторые SMTP-серверы блокируют или маскируют проверку `RCPT TO`, поэтому результат handshake может быть «неоднозначным».
- Для реального продакшна стоит добавить логирование в файл, retry-стратегию и экспорт метрик.
