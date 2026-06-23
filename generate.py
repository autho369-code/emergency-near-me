import json, os, shutil

with open('data.json') as f:
    data = json.load(f)

with open('template.html', encoding='utf-8') as f:
    template = f.read()

services = data['services']

# Emergency tips per service
tips = {
    'plumber': ['Active leaks or burst pipes','Sewer or drain backup','Water heater failure','Flooding or water shutoff issues','Frozen or broken pipes','Gas line concerns'],
    'electrician': ['Power outage limited to your property','Burning smell from outlets or panels','Sparking outlets','Breaker or panel emergency','Exposed or damaged wiring','Electrical fire concerns'],
    'hvac': ['No heat in dangerous cold','No AC in extreme heat','System failure','Unusual burning smell or electrical issue','Carbon monoxide alarm','Refrigerant leak'],
    'locksmith': ['Locked out of your home or vehicle','Broken key in lock','Break-in or damage requiring immediate security','Malfunctioning electronic lock','Lost all copies of a key','Safe will not open'],
    'mechanic': ['Dead battery or jump start needed','Flat tire on the road','Engine failure or will not start','Overheated engine','Brake failure','Check engine light with drivability issues'],
    'roofer': ['Active roof leak during rain','Storm or wind damage','Fallen tree or debris on roof','Missing shingles exposing underlayment','Water coming through ceiling','Ice dam causing interior damage'],
    'appliance': ['Refrigerator stopped cooling — food at risk','Washing machine flooding','Oven or stove will not heat','Dryer not working with wet laundry','Dishwasher leaking','Water heater failure'],
    'pest-control': ['Wasp or bee nest near entryways','Rodent inside living space','Bed bug discovery','Termite swarm or visible damage','Cockroach infestation','Ants invading food areas'],
    'water-damage': ['Burst pipe flooding','Sewage backup','Water heater rupture','Storm flooding','Roof leak with interior damage','Mold growth from water intrusion'],
}

svc_options = ''.join(f'<option value="{s["id"]}">{s["name"]}</option>' for s in services)

for state_key, state_info in data["states"].items():
    state_abbr = state_info["abbr"]
    for city_slug, city in state_info["cities"].items():
        for svc in services:
            svc_id = svc['id']
            other = [s for s in services if s['id'] != svc_id]
            alt_links = '\n      '.join(f'<a href="/{state_key}/{city_slug}/{s["id"]}/" class="alt-link">{s["name"]}</a>' for s in other)
            svc_opts = svc_options.replace(f'value="{svc_id}"', f'value="{svc_id}" selected')
            tip_html = '\n      '.join(f'<li>{t}</li>' for t in tips.get(svc_id, ['Emergency service needed']))

            html = template
            html = html.replace('__TITLE__', f'Emergency {svc["name"]} in {city["name"]}, {state_abbr} | CallNowService')
            html = html.replace('__META_DESC__', f'Find approved emergency {svc["name"].lower()} serving {city["name"]}, {state_abbr}. View up to five provider listings and contact businesses directly by phone, website, or booking page.')
            html = html.replace('__STATE_NAME__', state_info["name"])
            html = html.replace('__STATE_SLUG__', state_key)
            html = html.replace('__STATE_ABBR__', state_abbr)
            html = html.replace('__CITY_NAME__', city['name'])
            html = html.replace('__CITY_SLUG__', city_slug)
            html = html.replace('__SERVICE_NAME__', svc['name'])
            html = html.replace('__SERVICE_SLUG__', svc_id)
            html = html.replace('__SERVICE_PLURAL__', svc.get('plural', svc['name'].lower() + 's'))
            html = html.replace('__SERVICE_OPTIONS__', svc_opts)
            html = html.replace('__ALTERNATE_LINKS__', alt_links)
            html = html.replace('__EMERGENCY_TIPS__', tip_html)

            dir_path = os.path.join(state_key, city_slug, svc_id)
            os.makedirs(dir_path, exist_ok=True)
            with open(os.path.join(dir_path, 'index.html'), 'w', encoding='utf-8') as f:
                f.write(html)

print(f'Done! {len(data["states"])} states regenerated.')
print(f'Each page loads providers dynamically from providers.json')
