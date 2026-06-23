#!/usr/bin/env python3
"""
CallNowService — Real Provider Scraper
Finds actual emergency service providers via web search,
extracts name, phone, website, email.
Adds to providers.json with status=trial_created.
Usage: python scrape_providers.py Chicago plumber
"""

import json, sys, os, re
from datetime import datetime, timedelta

PROVIDERS_FILE = os.path.join(os.path.dirname(__file__), 'providers.json')
DATA_FILE = os.path.join(os.path.dirname(__file__), 'data.json')

SERVICE_KEYWORDS = {
    'plumber': 'emergency plumber',
    'electrician': 'emergency electrician',
    'hvac': 'emergency hvac heating cooling',
    'locksmith': 'emergency locksmith',
    'roofer': 'emergency roofer roofing',
    'mechanic': 'emergency mechanic roadside',
    'appliance': 'emergency appliance repair',
    'pest-control': 'emergency pest control exterminator',
    'water-damage': 'water damage restoration emergency',
}

SERVICE_NAMES = {
    'plumber':'Plumber','electrician':'Electrician','hvac':'HVAC',
    'locksmith':'Locksmith','roofer':'Roofer','mechanic':'Mechanic',
    'appliance':'Appliance Repair','pest-control':'Pest Control',
    'water-damage':'Water Damage',
}

BLOCKED_DOMAINS = ['yelp.com','facebook.com','yellowpages.com','angi.com','thumbtack.com',
    'nextdoor.com','bbb.org','homeadvisor.com','angi.com','mapquest.com',
    'superpages.com','manta.com','chamberofcommerce.com','cylex.us.com']

def load_json(path):
    with open(path) as f: return json.load(f)

def save_json(data, path):
    with open(path, 'w') as f: json.dump(data, f, indent=2)

def extract_email_from_text(text):
    """Extract valid business email from text, filtering out generic ones"""
    emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.]+', text)
    # Filter out common CDN/protection emails
    skip = ['example.com','domain.com','sentry.io','cloudfront.net','cdn','pixel']
    for e in emails:
        if not any(s in e.lower() for s in skip):
            return e.lower()
    return ''

def extract_phone(text):
    """Extract US phone number"""
    phones = re.findall(r'\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}', text)
    return phones[0] if phones else ''

def scrape_providers(city, service, max_results=5):
    """
    Scrape real providers using web search.
    This is called from execute_code which has access to web_search tools.
    """
    import subprocess
    results = []
    
    # Use curl to search DuckDuckGo (HTML version, no JS required)
    keyword = SERVICE_KEYWORDS.get(service, f'{service}')
    query = f'"{keyword}" {city} phone'
    
    try:
        # Primary: try DuckDuckGo HTML search
        import urllib.parse
        qs = urllib.parse.quote(query)
        cmd = f'curl -s -L --max-time 15 "https://lite.duckduckgo.com/lite/?q={qs}" 2>/dev/null'
        output = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=20).stdout
        
        # Parse results: find links and snippets
        links = re.findall(r'<a[^>]+href="(https?://[^"]+)"[^>]*>([^<]+)</a>', output)
        
        for url, title in links:
            if len(results) >= max_results: break
            if any(d in url.lower() for d in BLOCKED_DOMAINS): continue
            
            name = title.strip()
            if not name or len(name) < 5: continue
            if name.lower() in ['cached','more results','next','previous']: continue
            
            # Try to extract phone from the same page
            phone = extract_phone(output)
            email = extract_email_from_text(output)
            
            results.append({'name': name, 'website': url, 'phone': phone, 'email': email})
            
    except Exception as e:
        print(f'  Search error: {e}')
    
    # If DuckDuckGo failed, try alternative
    if not results:
        try:
            cmd = f'curl -s -L --max-time 15 "https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}" 2>/dev/null'
            output = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=20).stdout
            
            titles = re.findall(r'class="result__title"[^>]*>.*?<a[^>]*>([^<]+)</a>', output, re.DOTALL)
            snippets = re.findall(r'class="result__snippet"[^>]*>([^<]+)', output)
            urls = re.findall(r'class="result__url"[^>]*>([^<]+)', output)
            
            for i, title in enumerate(titles[:max_results]):
                name = title.strip()
                if len(name) < 5: continue
                phone = extract_phone(snippets[i] if i < len(snippets) else '')
                email = extract_email_from_text(snippets[i] if i < len(snippets) else '')
                url = urls[i] if i < len(urls) else ''
                if url and not url.startswith('http'): url = 'https://' + url
                
                # Clean name
                name = name.split('|')[0].split(' — ')[0].split(' - ')[0].strip()
                
                results.append({'name': name, 'website': url, 'phone': phone, 'email': email})
        except Exception as e:
            print(f'  Fallback search error: {e}')
    
    return results[:max_results]

def add_to_database(city_name, service, providers):
    """Add scraped providers to providers.json as trial_created"""
    data = load_json(PROVIDERS_FILE)
    
    # Find city slug
    cities_data = load_json(DATA_FILE)
    city_slug = None
    state_slug = None
    lower = city_name.lower().strip()
    
    for sk, st in cities_data['states'].items():
        for ck, c in st['cities'].items():
            if c['name'].lower() == lower:
                city_slug = ck
                state_slug = sk
                break
        if city_slug: break
    
    if not city_slug:
        # Try partial match
        for sk, st in cities_data['states'].items():
            for ck, c in st['cities'].items():
                if lower in c['name'].lower() or c['name'].lower() in lower:
                    city_slug = ck
                    state_slug = sk
                    break
            if city_slug: break
    
    if not city_slug:
        print(f'  City "{city_name}" not in database')
        return 0
    
    vendors = data.get(city_slug, {}).get(service, [])
    
    added = 0
    for p in providers:
        for v in vendors:
            name = v.get('provider_name', '')
            if not name or name in ('Available', ''):
                trial_exp = (datetime.now() + timedelta(hours=72)).strftime('%Y-%m-%dT%H:%M')
                v['provider_name'] = p.get('name', '')
                v['provider_phone'] = p.get('phone', '')
                v['provider_website'] = p.get('website', '')
                v['provider_email'] = p.get('email', '')
                v['status'] = 'trial_created'
                v['trial_expires'] = trial_exp
                v['trial_started'] = datetime.now().strftime('%Y-%m-%dT%H:%M')
                added += 1
                print(f'  + {p["name"]}')
                if p.get('phone'): print(f'    📞 {p["phone"]}')
                if p.get('email'): print(f'    ✉️ {p["email"]}')
                if p.get('website'): print(f'    🌐 {p["website"]}')
                break
    
    if added > 0:
        data['_meta']['updated'] = datetime.now().strftime('%Y-%m-%d')
        save_json(data, PROVIDERS_FILE)
    
    return added

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python scrape_providers.py <city> <service>')
        print('Example: python scrape_providers.py Chicago plumber')
        sys.exit(1)
    
    city = sys.argv[1]
    service = sys.argv[2]
    
    if service not in SERVICE_NAMES:
        print(f'Unknown service: {service}')
        print(f'Available: {", ".join(SERVICE_NAMES.keys())}')
        sys.exit(1)
    
    print(f'Scraping: {SERVICE_NAMES[service]} in {city}...')
    providers = scrape_providers(city, service, max_results=5)
    
    if not providers:
        print('No providers found.')
        sys.exit(0)
    
    print(f'\nFound {len(providers)} providers. Adding to database...')
    added = add_to_database(city, service, providers)
    print(f'\n{added} trial providers added (72hr expiration).')
