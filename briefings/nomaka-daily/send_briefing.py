from __future__ import annotations

import os
import smtplib
import ssl
import sys
from dataclasses import dataclass
from datetime import datetime
from email.message import EmailMessage
from typing import Any
from zoneinfo import ZoneInfo

from openai import OpenAI


LISBON_TZ = ZoneInfo("Europe/Lisbon")
DEFAULT_MODEL = "gpt-5"


@dataclass(frozen=True)
class SmtpConfig:
    host: str
    port: int
    username: str
    password: str
    sender: str
    recipient: str
    cc: str | None


def env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None or value == "":
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def build_prompt(today: str) -> str:
    return f"""
Create Nomaka's daily intelligence briefing for {today}.

Audience:
- Primary: operations manager
- Secondary: CEO-level decision-making

Monitor these topics:
- industry news
- supplier risks
- logistics disruptions
- regulatory updates
- competitor signals
- market developments relevant to Nomaka

Rules:
- Avoid noise.
- Prefer material business implications.
- Focus on margin, supply continuity, lead times, inventory risk, channel performance, geographic exposure, capital allocation, brand positioning, and major macro or geopolitical shifts.
- If there are no major developments, still produce a short briefing that says no material changes were found.
- Keep the final briefing under 500 words unless there is a major event.
- Use this structure exactly:
1. What matters today
2. Why it matters
3. Recommended action
4. Ignore / no-action items
5. Watchlist for the next 7 days
- End with a 'Sources' section that includes clickable Markdown links.
""".strip()


def should_run_now() -> bool:
    if os.getenv("GITHUB_EVENT_NAME") != "schedule":
        return True
    now = datetime.now(LISBON_TZ)
    return now.hour == 8


def collect_urls(node: Any, found: dict[str, str]) -> None:
    if isinstance(node, dict):
        url = node.get("url")
        title = node.get("title")
        if isinstance(url, str) and url:
            found.setdefault(url, title if isinstance(title, str) and title else url)
        for value in node.values():
            collect_urls(value, found)
        return
    if isinstance(node, list):
        for item in node:
            collect_urls(item, found)


def ensure_sources_section(body: str, response_dump: dict[str, Any]) -> str:
    if "Sources" in body:
        return body
    found: dict[str, str] = {}
    collect_urls(response_dump, found)
    if not found:
        return body
    lines = [body.rstrip(), "", "Sources"]
    for url, title in found.items():
        lines.append(f"- [{title}]({url})")
    return "\n".join(lines).strip()


def generate_briefing(today: str) -> str:
    client = OpenAI(api_key=env("OPENAI_API_KEY"))
    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL") or DEFAULT_MODEL,
        reasoning={"effort": "low"},
        tool_choice="auto",
        include=["web_search_call.action.sources"],
        tools=[
            {
                "type": "web_search",
                "user_location": {
                    "type": "approximate",
                    "country": "PT",
                    "city": "Lisbon",
                    "region": "Lisbon",
                    "timezone": "Europe/Lisbon",
                },
            }
        ],
        input=build_prompt(today),
    )

    briefing = (response.output_text or "").strip()
    if not briefing:
        raise RuntimeError("OpenAI returned an empty briefing.")
    return ensure_sources_section(briefing, response.model_dump())


def smtp_config() -> SmtpConfig:
    username = env("SMTP_USERNAME")
    return SmtpConfig(
        host=env("SMTP_HOST"),
        port=int(env("SMTP_PORT", "465")),
        username=username,
        password=env("SMTP_PASSWORD"),
        sender=os.getenv("SMTP_FROM", username),
        recipient=env("BRIEFING_TO"),
        cc=os.getenv("BRIEFING_CC"),
    )


def send_email(subject: str, body: str, config: SmtpConfig) -> None:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = config.sender
    msg["To"] = config.recipient
    if config.cc:
        msg["Cc"] = config.cc
    msg.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(config.host, config.port, context=context) as smtp:
        smtp.login(config.username, config.password)
        smtp.send_message(msg)


def write_summary(subject: str, body: str) -> None:
    summary_path = os.getenv("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return
    with open(summary_path, "a", encoding="utf-8") as handle:
        handle.write(f"## {subject}\n\n")
        handle.write("```text\n")
        handle.write(body)
        handle.write("\n```\n")


def main() -> int:
    if not should_run_now():
        now = datetime.now(LISBON_TZ).isoformat(timespec="minutes")
        print(f"Skipping run because Lisbon time is {now}, not 08:xx.")
        return 0

    today = datetime.now(LISBON_TZ).date().isoformat()
    subject = f"Nomaka Daily Intelligence Briefing - {today}"
    briefing = generate_briefing(today)
    send_email(subject, briefing, smtp_config())
    write_summary(subject, briefing)
    print(subject)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
