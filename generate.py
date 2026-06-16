import json, os, shutil

with open('data.json') as f:
    data = json.load(f)

with open('template.html', encoding='utf-8') as f:
    template = f.read()

template = template.replace('_WARNING_', '\u26a0\ufe0f')
template = template.replace('_RED_', '\U0001f534')
template = template.replace('_CLOCK_', '\u23f1\ufe0f')
template = template.replace('_LICENSE_', '\U0001faaa')
template = template.replace('_MONEY_', '\U0001f4b0')
template = template.replace('_STAR_', '\u2605')
template = template.replace('_CITY_', '\U0001f3d9\ufe0f')
template = template.replace('_TOOLS_', '\U0001f6e0\ufe0f')
template = template.replace('_COPY_', '\u00a9')
template = template.replace('_BACK_', '\u2190')

services = data['services']

service_content = {
    'plumber': {
        'emergency_examples': 'Burst pipes, no water, sewer backup, major leaks, no hot water, gas smell, sump pump failure, clogged drains, water heater failure',
        'hero_desc': '__CITY_NAME__ burst pipe at 3am? No hot water in winter? Sewer backing up? Our emergency plumbers are ready now. Licensed, insured, 30-minute response.',
        'items': '<div class="svc"><h3>Burst Pipes</h3><p>Emergency shut-off & repair</p></div><div class="svc"><h3>Water Heater</h3><p>Repair or same-day replacement</p></div><div class="svc"><h3>Clogged Drains</h3><p>Hydro-jetting & camera inspection</p></div><div class="svc"><h3>Sewer Line</h3><p>Backup & collapse repair</p></div><div class="svc"><h3>Leak Detection</h3><p>Electronic location & repair</p></div><div class="svc"><h3>Sump Pump</h3><p>Failure & battery backup</p></div><div class="svc"><h3>Gas Line</h3><p>Leak detection & repair</p></div><div class="svc"><h3>Fixtures</h3><p>Toilets, faucets, showers</p></div>'
    },
    'electrician': {
        'emergency_examples': 'Power outage, sparking outlets, burning smell, circuit breaker keeps tripping, exposed wiring, no power to essential appliances, electrical fire',
        'hero_desc': '__CITY_NAME__ lights out? Breaker tripping? Sparking outlet? Our emergency electricians respond in 30 minutes or less. Licensed, insured, 24/7.',
        'items': '<div class="svc"><h3>Power Outage</h3><p>Partial or full outage repair</p></div><div class="svc"><h3>Sparking Outlets</h3><p>Diagnosis & replacement</p></div><div class="svc"><h3>Electrical Fire</h3><p>Emergency disconnect & repair</p></div><div class="svc"><h3>Breaker Issues</h3><p>Panel repair & upgrade</p></div><div class="svc"><h3>Lighting</h3><p>Emergency lighting repair</p></div><div class="svc"><h3>Generator</h3><p>Backup power installation</p></div><div class="svc"><h3>Rewiring</h3><p>Old/faulty wiring replacement</p></div><div class="svc"><h3>Panel Upgrade</h3><p>Service panel replacement</p></div>'
    },
    'locksmith': {
        'emergency_examples': 'Locked out of house/car, broken key in lock, break-in damage, malfunctioning lock, lost keys, safe will not open, need immediate rekey',
        'hero_desc': '__CITY_NAME__ locked out? Key broke in the lock? Break-in damage? Our emergency locksmiths arrive in 30 minutes or less. 24/7 mobile service.',
        'items': '<div class="svc"><h3>Home Lockout</h3><p>Non-destructive entry</p></div><div class="svc"><h3>Car Lockout</h3><p>All makes & models</p></div><div class="svc"><h3>Broken Key</h3><p>Extraction & replacement</p></div><div class="svc"><h3>Lock Change</h3><p>After break-in or lost keys</p></div><div class="svc"><h3>Safe Opening</h3><p>Digital & combination safes</p></div><div class="svc"><h3>Commercial</h3><p>High-security lock systems</p></div><div class="svc"><h3>Rekey</h3><p>Same-day rekey service</p></div><div class="svc"><h3>Smart Locks</h3><p>Access control & installation</p></div>'
    },
    'hvac': {
        'emergency_examples': 'No heat in winter, no AC in summer, burning smell from vents, carbon monoxide alarm, frozen AC unit, furnace failure, gas smell from HVAC',
        'hero_desc': '__CITY_NAME__ no heat in a winter freeze? AC dead in a heatwave? Our emergency HVAC technicians respond in 30 minutes. 24/7 heating & cooling repair.',
        'items': '<div class="svc"><h3>Furnace Repair</h3><p>No heat? Emergency fix</p></div><div class="svc"><h3>AC Repair</h3><p>No cooling? Same-day service</p></div><div class="svc"><h3>Thermostat</h3><p>Malfunction diagnosis & fix</p></div><div class="svc"><h3>Air Handler</h3><p>Motor & blower repair</p></div><div class="svc"><h3>Heat Pump</h3><p>Winter & summer emergency</p></div><div class="svc"><h3>Ductwork</h3><p>Leak repair & sealing</p></div><div class="svc"><h3>CO Alarm</h3><p>Immediate inspection & fix</p></div><div class="svc"><h3>Refrigerant</h3><p>Leak repair & recharge</p></div>'
    },
    'roofer': {
        'emergency_examples': 'Roof leak during storm, wind damage, fallen tree on roof, missing shingles, water coming through ceiling, ice dam, emergency tarping needed',
        'hero_desc': '__CITY_NAME__ water coming through the ceiling? Storm rip off shingles? Our emergency roofers respond fast with emergency tarping and permanent repair.',
        'items': '<div class="svc"><h3>Leak Repair</h3><p>Emergency patch & seal</p></div><div class="svc"><h3>Storm Damage</h3><p>Wind & hail emergency repair</p></div><div class="svc"><h3>Tree Damage</h3><p>Impact assessment & tarping</p></div><div class="svc"><h3>Emergency Tarp</h3><p>Immediate water protection</p></div><div class="svc"><h3>Missing Shingles</h3><p>Replacement & matching</p></div><div class="svc"><h3>Ice Dam</h3><p>Removal & prevention</p></div><div class="svc"><h3>Ceiling Leak</h3><p>Trace source & fix</p></div><div class="svc"><h3>Inspection</h3><p>Full roof assessment</p></div>'
    },
    'mechanic': {
        'emergency_examples': 'Dead battery, flat tire, engine failure, car will not start, overheated engine, check engine light, brake failure, alternator failure',
        'hero_desc': '__CITY_NAME__ dead battery? Flat tire on the highway? Engine will not start? Our emergency mechanics are on the way. 24/7 roadside assistance, 30-minute response.',
        'items': '<div class="svc"><h3>Dead Battery</h3><p>Jump start & replacement</p></div><div class="svc"><h3>Flat Tire</h3><p>Change & tire repair</p></div><div class="svc"><h3>Engine Failure</h3><p>Diagnosis & emergency repair</p></div><div class="svc"><h3>Car Will Not Start</h3><p>Starter, alternator, fuel issues</p></div><div class="svc"><h3>Overheated Engine</h3><p>Coolant leak & radiator fix</p></div><div class="svc"><h3>Brake Failure</h3><p>Emergency brake repair</p></div><div class="svc"><h3>Lockout Service</h3><p>Keys locked in car</p></div><div class="svc"><h3>Fuel Delivery</h3><p>Ran out of gas? We bring it</p></div>'
    },
    'appliance': {
        'emergency_examples': 'Refrigerator stopped cooling, washing machine flooding, oven will not heat, dryer not working, dishwasher leak, freezer failure, food spoiling',
        'hero_desc': '__CITY_NAME__ fridge died with $500 in groceries? Washing machine flooding the laundry room? Our emergency appliance repair techs respond fast. Same-day service.',
        'items': '<div class="svc"><h3>Refrigerator</h3><p>Not cooling? Emergency fix</p></div><div class="svc"><h3>Washing Machine</h3><p>Leak, spin failure, no drain</p></div><div class="svc"><h3>Oven/Stove</h3><p>Will not heat? Same-day repair</p></div><div class="svc"><h3>Dryer</h3><p>No heat, will not spin</p></div><div class="svc"><h3>Dishwasher</h3><p>Leak, will not drain</p></div><div class="svc"><h3>Freezer</h3><p>Thawing out? Emergency service</p></div><div class="svc"><h3>Water Heater</h3><p>No hot water? We fix it</p></div><div class="svc"><h3>Garbage Disposal</h3><p>Jammed or broken? Fast fix</p></div>'
    },
    'pest-control': {
        'emergency_examples': 'Wasp nest inside or near entry, rodent in the house, bed bug discovery, termite swarm, cockroach infestation, ants invading kitchen, bee hive in wall',
        'hero_desc': '__CITY_NAME__ wasps in the house? Rodent in the kitchen? Our emergency pest control teams respond within the hour. Same-day extermination. 24/7 availability.',
        'items': '<div class="svc"><h3>Wasp/Bee Removal</h3><p>Nest removal & prevention</p></div><div class="svc"><h3>Rodent Control</h3><p>Mice, rats, squirrels</p></div><div class="svc"><h3>Bed Bugs</h3><p>Heat treatment & chemical</p></div><div class="svc"><h3>Termites</h3><p>Inspection & colony treatment</p></div><div class="svc"><h3>Roaches</h3><p>Infestation treatment</p></div><div class="svc"><h3>Ants</h3><p>Colony location & elimination</p></div><div class="svc"><h3>Wildlife</h3><p>Raccoon, skunk, snake removal</p></div><div class="svc"><h3>Fumigation</h3><p>Whole-home treatment</p></div>'
    },
    'water-damage': {
        'emergency_examples': 'Burst pipe flooding, sewage backup, water heater rupture, storm flooding, basement flood, roof leak water damage, appliance overflow, mold growth',
        'hero_desc': '__CITY_NAME__ water flooding your home? Sewage backing up? Our emergency restoration teams respond in 30 minutes. Water extraction, drying, and full restoration.',
        'items': '<div class="svc"><h3>Water Extraction</h3><p>Industrial pumps & vacuums</p></div><div class="svc"><h3>Sewage Cleanup</h3><p>Hazmat-trained, full sanitation</p></div><div class="svc"><h3>Structural Drying</h3><p>Commercial dehumidifiers & fans</p></div><div class="svc"><h3>Mold Remediation</h3><p>Detection, removal, prevention</p></div><div class="svc"><h3>Flood Damage</h3><p>Basement & ground floor restoration</p></div><div class="svc"><h3>Fire & Smoke</h3><p>Post-fire water damage cleanup</p></div><div class="svc"><h3>Pipe Burst</h3><p>Emergency shut-off & dry-out</p></div><div class="svc"><h3>Insurance Claims</h3><p>Direct billing & documentation</p></div>'
    },
}

# State abbreviation mapping
state_abbr = {}
for state_key, state_info in data["states"].items():
    state_abbr[state_key] = state_info["name"]

# Clean old directories
existing_dirs = [d for d in os.listdir('.') if os.path.isdir(d) and d not in ['.git','node_modules','__pycache__','.hermes']]
for d in existing_dirs:
    if d in data["states"] or d in ['data.json','template.html','generate.py','index.html','providers.json','dashboard.html','ops.bat','outreach_emails.txt','robots.txt','sitemap.xml','billing_report.txt','AGENT_COMMANDS.md','SEARCH_CRITERIA.md']:
        continue
    shutil.rmtree(d, ignore_errors=True)

total = 0
ext_map = {'plumber':'0199','electrician':'0200','locksmith':'0300','hvac':'0400','roofer':'0500','mechanic':'0600','appliance':'0700','pest-control':'0800','water-damage':'0900'}

for state_key, state_info in data["states"].items():
    state_name = state_info["name"]
    state_abbr_code = state_info["abbr"]
    
    for city_slug, city in state_info["cities"].items():
        for svc in services:
            svc_id = svc['id']
            sc = service_content.get(svc_id, {})

            # Nearby links (other services in same city)
            nearby = []
            for other in services:
                if other['id'] != svc_id:
                    nearby.append(f'<a href="/{state_key}/{city_slug}/{other["id"]}/">{other["icon"]} Emergency {other["name"]}</a>')

            n_list = '\n    '.join([f'<li>{n}</li>' for n in city['neighborhoods']])
            
            phone = city['phones'].get(svc_id, '')
            area = city['areaCode']
            phone_display = f'({area}) 555-{ext_map.get(svc_id, "0000")}'

            html = template
            html = html.replace('__TITLE__', f'Emergency {svc["name"]} {city["name"]}, {state_abbr_code} \u2014 24/7 Services | Call Now')
            html = html.replace('__DESCRIPTION__', f'Emergency {svc["name"].lower()} in {city["name"]}, {state_abbr_code} available 24/7. {sc.get("emergency_examples","")[:120]}. Licensed & insured. 30-minute response. Call now.')
            html = html.replace('__STATE_NAME__', state_name)
            html = html.replace('__STATE_SLUG__', state_key)
            html = html.replace('__CITY_NAME__', city['name'])
            html = html.replace('__CITY_STATE__', state_abbr_code)
            html = html.replace('__CITY_SLUG__', city_slug)
            html = html.replace('__SERVICE_NAME__', svc['name'])
            html = html.replace('__SERVICE_SLUG__', svc_id)
            html = html.replace('__PHONE__', phone)
            html = html.replace('__PHONE_DISPLAY__', phone_display)
            html = html.replace('__AVG_COST__', svc['avgCost'])
            html = html.replace('__HERO_DESC__', sc.get('hero_desc','').replace('__CITY_NAME__', city['name']))
            html = html.replace('__EMERGENCY_EXAMPLES__', sc.get('emergency_examples',''))
            html = html.replace('__SERVICE_ITEMS__', sc.get('items',''))
            html = html.replace('__NEIGHBORHOODS__', json.dumps(city['neighborhoods']))
            html = html.replace('__NEIGHBORHOOD_LIST__', n_list)
            html = html.replace('__NEARBY_LINKS__', '\n    '.join(nearby))

            dir_path = os.path.join(state_key, city_slug, svc_id)
            os.makedirs(dir_path, exist_ok=True)
            with open(os.path.join(dir_path, 'index.html'), 'w', encoding='utf-8') as f:
                f.write(html)
            total += 1

print(f'Done! {total} pages generated across {len(data["states"])} states.')
