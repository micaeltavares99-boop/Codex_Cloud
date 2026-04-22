# Nomaka Repo-Backed Briefing

This repo now includes a minimal prompt pack for running the Nomaka daily intelligence briefing from a GitHub-backed Codex Cloud environment.

## Files

- `AGENTS.md`: repo-level instructions for Codex.
- `briefings/nomaka-daily/BRIEFING_TASK.md`: the briefing brief/specification.

## How to use this with Codex Cloud

1. Add your GitHub repo as the remote for this local folder.
2. Commit and push the briefing files.
3. Open Codex at `https://chatgpt.com/codex`.
4. Connect GitHub if you have not already.
5. Create a cloud environment for this repository in Codex settings.
6. Use internet access for the research step, and keep Gmail available for delivery.
7. Start a cloud task that tells Codex to use `briefings/nomaka-daily/BRIEFING_TASK.md` and send the briefing email.

## Important limitation

Repository-backed cloud execution removes the need for your PC to stay on for the task itself, but your current desktop app automation is still a local app automation. If you want the daily schedule to stop depending on the desktop app, the scheduling layer also needs to move off the local app flow.
