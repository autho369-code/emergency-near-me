import json, os, shutil

with open('data.json') as f:
    data = json.load(f)

with open('template.html', encoding='utf-8') as f:
    template = f.read()

services = data['services']

# Service-specific content for meta/SEO
service_content = {
    'plumber': 'Burst pipes, no water, sewer backup, major leaks, no hot water, gas smell, sump pump failure, clogged drains, water heater failure',
    'electrician': 'Power outage, sparking outlets, burning smell, circuit breaker keeps tripping, exposed wiring, no power to essential appliances, electrical fire',
    'locksmith': 'Locked out of house/car, broken key in lock, break-in damage, malfunctioning lock, lost keys, safe will not open, need immediate rekey',
    'hvac': 'No heat in winter, no AC in summer, burning smell from vents, carbon monoxide alarm, frozen AC unit, furnace failure, gas smell from HVAC',
    'roofer': 'Roof leak during storm, wind damage, fallen tree on roof, missing shingles, water coming through ceiling, ice dam, emergency tarping needed',
    'mechanic': 'Dead battery, flat tire, engine failure, car will not start, overheated engine, check engine light, brake failure, alternator failure',
    'appliance': 'Refrigerator stopped cooling, washing machine flooding, oven will not heat, dryer not working, dishwasher leak, freezer failure, food spoiling',
    'pest-control': 'Wasp nest inside or near entry, rodent in the house, bed bug discovery, termite swarm, cockroach infestation, ants invading kitchen, bee hive in wall',
    'water-damage': 'Burst pipe flooding, sewage backup, water heater rupture, storm flooding, basement flood, roof leak water damage, appliance overflow, mold growth',
}

# State abbreviation mapping
state_names = {}
for state_key, state_info in data["states"].items():
    state_names[state_key] = state_info["name"]

# Clean old state directories
existing_dirs = [d for d in os.listdir('.') if os.path.isdir(d) and d not in ['.git','node_modules','__pycache__','.hermes','api']]
for d in existing_dirs:
    if d in data["states"] or d in ['.git','node_modules','__pycache__','.hermes']:
        continue
    if os.path.isfile(d):
        continue
    shutil.rmtree(d, ignore_errors=True)

total = 0

for state_key, state_info in data["states"].items():
    state_name = state_info["name"]
    state_abbr = state_info["abbr"]
    
    for city_slug, city in state_info["cities"].items():
        for svc in services:
            svc_id = svc['id']
            sc_content = service_content.get(svc_id, '')

            # Nearby links (other services in same city)
            nearby = []
            for other in services:
                if other['id'] != svc_id:
                    nearby.append(f'<a href="/{state_key}/{city_slug}/{other["id"]}/">{other["icon"]} {other["name"]}</a>')

            html = template
            html = html.replace('__TITLE__', f'Emergency {svc["name"]} {city["name"]}, {state_abbr} — 24/7 Services | Call Now')
            html = html.replace('__DESCRIPTION__', f'Emergency {svc["name"].lower()} in {city["name"]}, {state_abbr}. 5 verified 24/7 providers. {sc_content[:120]}. Licensed & insured. Direct business routing. Flat monthly pricing.')
            html = html.replace('__STATE_NAME__', state_name)
            html = html.replace('__STATE_SLUG__', state_key)
            html = html.replace('__STATE_ABBR__', state_abbr)
            html = html.replace('__CITY_NAME__', city['name'])
            html = html.replace('__CITY_SLUG__', city_slug)
            html = html.replace('__SERVICE_NAME__', svc['name'])
            html = html.replace('__SERVICE_SLUG__', svc_id)
            html = html.replace('__PHONE__', city['phones'].get(svc_id, ''))
            html = html.replace('__EMERGENCY_EXAMPLES__', sc_content)
            html = html.replace('__NEARBY_LINKS__', '\n      '.join(nearby))

            dir_path = os.path.join(state_key, city_slug, svc_id)
            os.makedirs(dir_path, exist_ok=True)
            with open(os.path.join(dir_path, 'index.html'), 'w', encoding='utf-8') as f:
                f.write(html)
            total += 1

print(f'Done! {total} pages generated across {len(data["states"])} states.')
print(f'Each page loads providers dynamically from providers.json')
print(f'AI crawler directives included on every page')
