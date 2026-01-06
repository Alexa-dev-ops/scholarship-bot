from agent import run_agent
from emailer import send_email

new_items, reminders = run_agent()

if new_items:
    body = "\n\n".join(
        f"{s['name']}\n{s['url']}" for s in new_items
    )
    send_email(
        "🎓 New Fully Funded UK Scholarships Found",
        body
    )

for r in reminders:
    send_email(
        f"⏰ Deadline Reminder ({r['days']} days left)",
        f"{r['name']}\n{r['url']}"
    )
