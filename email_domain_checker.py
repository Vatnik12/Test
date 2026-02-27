#!/usr/bin/env python3
"""Проверка email-адресов: DNS MX + SMTP handshake (без отправки письма)."""

from __future__ import annotations

import argparse
import re
import smtplib
import socket
from dataclasses import dataclass
from typing import Iterable, List

import dns.resolver


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass
class EmailCheckResult:
    email: str
    status: str
    mx_hosts: List[str]
    smtp_check: str


def load_emails(raw_items: Iterable[str]) -> List[str]:
    emails: List[str] = []
    for item in raw_items:
        candidate = item.strip()
        if not candidate:
            continue
        if EMAIL_RE.match(candidate):
            emails.append(candidate)
        else:
            emails.append(candidate)
    return emails


def resolve_mx(domain: str) -> List[str]:
    answers = dns.resolver.resolve(domain, "MX")
    records = sorted(answers, key=lambda r: r.preference)
    hosts = [str(r.exchange).rstrip(".") for r in records if str(r.exchange).strip(".")]
    return hosts


def smtp_user_check(email: str, mx_host: str, timeout: int = 8) -> str:
    sender_probe = "probe@example.com"
    try:
        with smtplib.SMTP(mx_host, 25, timeout=timeout) as smtp:
            smtp.ehlo_or_helo_if_needed()
            smtp.mail(sender_probe)
            code, message = smtp.rcpt(email)
            message_text = message.decode(errors="ignore") if isinstance(message, bytes) else str(message)
            if 200 <= code < 300:
                return f"SMTP: пользователь принят ({code} {message_text})"
            if code in {450, 451, 452, 550, 551, 552, 553, 554}:
                return f"SMTP: пользователь отклонен ({code} {message_text})"
            return f"SMTP: неоднозначный ответ ({code} {message_text})"
    except (smtplib.SMTPException, socket.timeout, OSError) as exc:
        return f"SMTP: ошибка handshake ({exc})"


def classify_domain(email: str) -> EmailCheckResult:
    if "@" not in email:
        return EmailCheckResult(email, "домен отсутствует", [], "SMTP: пропущено")

    _, domain = email.rsplit("@", 1)

    if not domain or "." not in domain:
        return EmailCheckResult(email, "домен отсутствует", [], "SMTP: пропущено")

    try:
        mx_hosts = resolve_mx(domain)
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
        return EmailCheckResult(email, "MX-записи отсутствуют или некорректны", [], "SMTP: пропущено")
    except dns.exception.DNSException:
        return EmailCheckResult(email, "домен отсутствует", [], "SMTP: пропущено")

    if not mx_hosts:
        return EmailCheckResult(email, "MX-записи отсутствуют или некорректны", [], "SMTP: пропущено")

    smtp_status = smtp_user_check(email, mx_hosts[0])
    return EmailCheckResult(email, "домен валиден", mx_hosts, smtp_status)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Проверка email-адресов: DNS MX + SMTP handshake (без отправки писем)",
    )
    parser.add_argument(
        "emails",
        nargs="*",
        help="Список email через пробел",
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Путь к txt-файлу с email-адресами (по одному в строке)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    raw_values: List[str] = []

    if args.file:
        with open(args.file, "r", encoding="utf-8") as file:
            raw_values.extend(file.readlines())

    raw_values.extend(args.emails)

    emails = load_emails(raw_values)
    if not emails:
        raise SystemExit("Передайте email-адреса через аргументы или --file")

    for email in emails:
        result = classify_domain(email)
        mx_str = ", ".join(result.mx_hosts) if result.mx_hosts else "-"
        print(f"{result.email}: {result.status}; MX: {mx_str}; {result.smtp_check}")


if __name__ == "__main__":
    main()
