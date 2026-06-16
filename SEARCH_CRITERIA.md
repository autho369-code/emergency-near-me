## Research Agent Search Criteria

The Research Agent (emn-research) uses the following search strategy
to find emergency service providers. These searches run every Monday
at 8am, finding 10 new providers per run.

### Primary Search Terms (tried in order)

1. "emergency [service] [city]" — highest intent
2. "[service] company [city]" — broad discover
3. "[service] [city] reviews" — finds highly-rated businesses
4. "best [service] [city] emergency" — quality signal

### Extraction Rules

For each result, extract:
- Business name (must be a real, verifiable business)
- Phone number (verified area code matches city)
- Website URL (if available)
- Email address (if publicly listed)
- Rating/reviews count (if available)

### Quality Filters

ACCEPT if:
- Phone number matches the city's area code
- Business has a verifiable website or Google Business Profile
- Business offers the specific service (e.g., don't list a general contractor as a plumber)

REJECT if:
- Only a generic listing (e.g., "Plumbers in X" aggregate page)
- Phone number is disconnected or toll-free only
- Business is clearly out of business or has no web presence
- Lead generation competitor (another directory site)

### What to Skip

- HomeAdvisor, Angi, Thumbtack, Yelp aggregate pages (not real businesses)
- National chains without local branches (unless they have a local office)
- Businesses with less than 3 reviews (unless nothing else available)

### After Finding a Provider

Update providers.json:
- provider_name: the verified business name
- provider_phone: the verified phone number
- provider_website: website URL if found
- status: change "searching" → "found"
- notes: date found and where info came from
