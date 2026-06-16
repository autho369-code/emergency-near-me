## Agent Command Reference

### 🔍 Research Agent (emn-research)
Trigger: Weekly Monday 8am OR manual Kanban task

Exact commands you can give:
- "Research Chicago plumbers" → finds 5 plumbers in Chicago
- "Research all services in Illinois" → fills all Illinois slots
- "Research HVAC in Chicago, Milwaukee, Detroit" → specific cities
- "Find 5 vendors for [city] [service]" → single slot

What it does:
1. Searches "emergency [service] [city]" on Google
2. Extracts business name, phone, website
3. Fills up to 5 vendor slots per service per city
4. Changes status: "searching" → "found"
5. Skips Yelp aggregates, toll-free numbers, dead businesses

### ✉️ Outreach Agent (emn-outreach)
Trigger: Weekly Wednesday 9am OR manual Kanban task

Exact commands:
- "Draft emails for Chicago" → drafts for all "found" Chicago providers
- "Draft emails for all Illinois" → all Illinois providers
- "Draft emails for [city] [service]" → single service

What it does:
1. Finds providers with status="found"
2. Drafts professional outreach email for each
3. Saves to outreach_emails.txt
4. Changes status: "found" → "contacted"

### 👁️ Supervisor Agent (emn-supervisor)
Trigger: Weekly Friday 10am OR manual Kanban task

Exact commands:
- "Status report" → full pipeline health report
- "Check Chicago" → status of all Chicago slots
- "Stalled providers" → list contacted providers with no response >7 days

What it does:
1. Reads providers.json
2. Checks pipeline health
3. Flags stalled providers
4. Reports what Mirsad should do next

### 💰 Billing Agent (emn-billing)
Trigger: 1st of each month OR manual Kanban task

Exact commands:
- "Generate invoice" → counts leads, calculates revenue
- "Check leads for Chicago" → specific city

What it does:
1. Checks countapi.xyz for click counts
2. Updates leads_month for active providers
3. Generates billing_report.txt

---

## Priority Order (hard-coded for Research Agent)

1. ILLINOIS (all cities)
2. Wisconsin, Indiana, Iowa, Missouri, Michigan
3. Rest of US alphabetically
