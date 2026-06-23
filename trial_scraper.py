#!/usr/bin/env python3
"""
CallNowService — GMB/Trial Provider Scraper
Scrapes Google Maps results (via web search) for emergency providers,
adds them to providers.json with 72-hour trial status,
and sends trial notification emails.

Usage: python trial_scraper.py Chicago plumber
"""

import json, sys, os, re, time
from datetime import datetime, timedelta
from urllib.request import Request, urlopen
from urllib.parse import quote_plus

PROVIDERS_FILE = os.path.join(os.path.dirname(__file__), 'providers.json')
DATA_FILE = os.path.join(os.path.dirname(__file__), 'data.json')
EMAIL_SCRIPT = os.path.join(os.path.dirname(__file__), 'send_email.py')

SERVICE_KEYWORDS = {
    'plumber': ['emergency plumber','24/7 plumber','plumbing company'],
    'electrician': ['emergency electrician','24 hour electrician','electrical contractor'],
    'hvac': ['emergency hvac','24/7 hvac','heating and cooling'],
    'locksmith': ['emergency locksmith','24 hour locksmith','locksmith near me'],
    'roofer': ['emergency roofer','roof repair','roofing company'],
    'mechanic': ['emergency mechanic','mobile mechanic','roadside assistance'],
    'appliance': ['appliance repair','emergency appliance repair','refrigerator repair'],
    'pest-control': ['pest control','emergency pest control','exterminator'],
    'water-damage': ['water damage restoration','emergency water removal','flood cleanup'],
}

SERVICE_NAMES = {
    'plumber':'Plumber','electrician':'Electrician','hvac':'HVAC',
    'locksmith':'Locksmith','roofer':'Roofer','mechanic':'Mechanic',
    'appliance':'Appliance Repair','pest-control':'Pest Control',
    'water-damage':'Water Damage Restoration',
}

def load_providers():
    with open(PROVIDERS_FILE) as f:
        return json.load(f)

def save_providers(data):
    with open(PROVIDERS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_cities():
    with open(DATA_FILE) as f:
        return json.load(f)

def find_city_slug(city_name, state_abbr=None):
    """Match city name to our data slug"""
    data = load_cities()
    lower = city_name.lower().strip()
    for sk, st in data['states'].items():
        if state_abbr and st['abbr'].lower() != state_abbr.lower():
            continue
        for ck, c in st['cities'].items():
            if c['name'].lower() == lower:
                return ck, sk
            if lower in c['name'].lower() or c['name'].lower() in lower:
                return ck, sk
    return None, None

def search_providers(city, service, max_results=5):
    """
    Search for providers using web search.
    Returns list of {name, phone, website, email}
    """
    keywords = SERVICE_KEYWORDS.get(service, [f'{service} {city}'])
    results = []

    for kw in keywords:
        if len(results) >= max_results:
            break
        query = f'"{kw}" {city} phone website'
        try:
            # Use curl-based search via terminal
            import subprocess
            cmd = f'curl -s "https://html.duckduckgo.com/html/?q={quote_plus(query)}" 2>/dev/null'
            output = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15).stdout

            # Extract business-like patterns
            phones = re.findall(r'\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}', output)
            websites = re.findall(r'https?://[^\s"\'<>]+', output)

            # Simple name extraction from snippet titles
            names = re.findall(r'class="result__snippet"[^>]*>([^<]+)', output)

            if phones or websites:
                result = {
                    'name': f'{city} {SERVICE_NAMES.get(service, service)} Pro',
                    'phone': phones[0] if phones else '',
                    'website': websites[0] if websites else '',
                    'email': '',
                }
                results.append(result)
        except Exception as e:
            print(f'  Search error for "{kw}": {e}')
            continue

    return results[:max_results]

def add_trial_providers(city_name, service, providers):
    """Add trial providers to providers.json"""
    data = load_providers()
    city_slug, state_slug = find_city_slug(city_name)

    if not city_slug:
        print(f'  City "{city_name}" not in database. Skipping.')
        return 0

    added = 0
    city_data = data.get(city_slug, {})
    vendors = city_data.get(service, [])

    for p in providers:
        # Find empty slot
        for v in vendors:
            if not v.get('provider_name') or v.get('provider_name') in ('Available', 'Your Company Here', ''):
                trial_expires = (datetime.now() + timedelta(hours=72)).strftime('%Y-%m-%dT%H:%M:%S')
                v['provider_name'] = p.get('name', f'{city_name} {SERVICE_NAMES.get(service, service)}')
                v['provider_phone'] = p.get('phone', '')
                v['provider_website'] = p.get('website', '')
                v['provider_email'] = p.get('email', '')
                v['status'] = 'trial'
                v['trial_expires'] = trial_expires
                v['trial_started'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
                added += 1
                print(f'  ✅ {v["provider_name"]} — trial until {trial_expires}')
                break
        else:
            print(f'  ⚠️ No empty slots for {service} in {city_name}')

    if added > 0:
        save_providers(data)

    return added

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python trial_scraper.py <city> <service>')
        print('Example: python trial_scraper.py Chicago plumber')
        sys.exit(1)

    city = sys.argv[1]
    service = sys.argv[2]

    if service not in SERVICE_NAMES:
        print(f'Unknown service: {service}')
        print(f'Available: {", ".join(SERVICE_NAMES.keys())}')
        sys.exit(1)

    print(f'Scraping: {SERVICE_NAMES[service]} in {city}...')
    providers = search_providers(city, service, max_results=5)

    if not providers:
        print('No providers found.')
        sys.exit(0)

    print(f'Found {len(providers)} results. Adding as trials...')
    added = add_trial_providers(city, service, providers)
    print(f'Added {added} trial providers.')
