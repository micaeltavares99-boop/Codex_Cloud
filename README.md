# Nomaka Repo-Backed Briefing

This repo now includes two ways to run the Nomaka daily intelligence briefing:

- Codex Cloud prompt files for repo-backed cloud tasks
- A GitHub Actions workflow that can generate and email the briefing on a daily schedule without your PC being on

## Files

- `AGENTS.md`: repo-level instructions for Codex
- `briefings/nomaka-daily/BRIEFING_TASK.md`: the briefing brief/specification
- `briefings/nomaka-daily/send_briefing.py`: the automation script
- `.github/workflows/nomaka-daily-briefing.yml`: the scheduled workflow

## What you need to add in GitHub Secrets

Go to the repository's Settings > Secrets and variables > Actions, then add:

- `OPENAI_API_KEY`: your OpenAI API key
- `OPENAI_MODEL`: optional, defaults to `gpt-5`
- `SMTP_HOST`: for Gmail, use `smtp.gmail.com`
- `SMTP_PORT`: for Gmail SSL, use `465`
- `SMTP_USERNAME`: the mailbox username
- `SMTP_PASSWORD`: the mailbox app password
- `SMTP_FROM`: optional sender address; if omitted it uses `SMTP_USERNAME`
- `BRIEFING_TO`: recipient email address, for example `Micael.tavares@nomaka.com`
- `BRIEFING_CC`: optional CC recipient

## Gmail note

If you use Gmail or Google Workspace, this workflow expects an app password rather than your normal sign-in password.

## How the schedule works

GitHub Actions cron uses UTC, not Lisbon time. The workflow runs twice per day in UTC and the Python script only sends the email when the local time in `Europe/Lisbon` is 08:xx. That keeps the send time aligned with Lisbon across daylight-saving changes.

## Manual run

In GitHub, open Actions, select `Nomaka Daily Briefing`, and use `Run workflow` to test it immediately after adding the secrets.

## Codex Cloud note

The repo is also ready for Codex Cloud tasks through `briefings/nomaka-daily/BRIEFING_TASK.md`. OpenAI's Codex web docs cover GitHub-backed cloud environments and repo checkout, but the daily email delivery in this repo is handled by GitHub Actions so it does not depend on the desktop app being open.
