import json, os, html

with open('data.json') as f:
    data = json.load(f)

with open('providers.json', encoding='utf-8') as f:
    providers_data = json.load(f)

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

VISIBLE_STATUSES = {'active', 'claimed', 'trial', 'trial_created', 'onboarding'}

svc_options = ''.join(f'<option value="{s["id"]}">{s["name"]}</option>' for s in services)


def render_provider_card(v, i, svc_name):
    name = html.escape(v.get('provider_name') or '')
    phone = v.get('provider_phone') or ''
    email = v.get('provider_email') or ''
    website = v.get('provider_website') or ''
    phone_ok = bool(phone) and 'XXXX' not in phone

    parts = [f'<div class="provider-card"><div class="rank">{i+1}</div><div class="card-info">'
             f'<h3>{name}<span class="badge">Approved provider</span></h3>'
             f'<div class="meta">{html.escape(svc_name)}</div>'
             f'<div class="desc">Emergency {html.escape(svc_name.lower())} services including urgent repairs, diagnostics, and 24/7 response.</div>'
             f'<div class="contact-links">']
    if phone_ok:
        parts.append(f'<span>\U0001F4DE <a href="tel:{html.escape(phone)}">{html.escape(phone)}</a></span>')
    if website:
        parts.append(f'<span>\U0001F310 <a href="{html.escape(website)}" target="_blank" rel="noopener">Website</a></span>')
    if email:
        parts.append(f'<span>✉️ <a href="mailto:{html.escape(email)}">Email</a></span>')
    parts.append('</div></div><div class="card-actions">')
    if phone_ok:
        parts.append(f'<a href="tel:{html.escape(phone)}" class="btn btn-call">Call Now</a>')
    if website:
        parts.append(f'<a href="{html.escape(website)}" target="_blank" rel="noopener" class="btn btn-secondary">Visit Website</a>')
    parts.append('</div></div>')
    return ''.join(parts)


def render_placeholder_card(i):
    return (f'<div class="provider-card placeholder-card"><div class="rank">{i+1}</div>'
            f'<div class="card-info"><h3>Additional provider listing coming soon</h3>'
            f'<div class="desc">We\'re expanding approved provider coverage for this city and service category.</div>'
            f'<a href="/providers">Are you a provider? Apply for this spot.</a></div><div class="card-actions"></div></div>')


def render_static_providers(city_slug, svc_id, svc_name):
    city = providers_data.get(city_slug)
    vendors = city.get(svc_id) if city else None
    if not vendors or not isinstance(vendors, list):
        return '', ''
    approved = [v for v in vendors if v.get('status') in VISIBLE_STATUSES and v.get('provider_name') and v.get('provider_name') != 'Available']
    if not approved:
        return '', ''
    cards = []
    for i, v in enumerate(vendors):
        name = v.get('provider_name') or ''
        is_visible = v.get('status') in VISIBLE_STATUSES and name and name != 'Available'
        cards.append(render_provider_card(v, i, svc_name) if is_visible else render_placeholder_card(i))
    return f'{len(approved)} of 5 spots filled', ''.join(cards)


def render_faq(svc_name, svc_plural, city_name, state_abbr):
    svc_lower = svc_name.lower()
    qa = [
        (f'How do I find an emergency {svc_lower} in {city_name}, {state_abbr} right now?',
         f'The listings above show up to five approved {svc_plural} serving {city_name}, {state_abbr}, each with a direct phone number and website. Call or visit their site directly — there\'s no form to fill out and no wait for a callback.'),
        (f'Is CallNowService free to use?',
         f'Yes. Finding and contacting {svc_plural} through CallNowService is free for customers. There are no lead fees, no bidding, and no membership required.'),
        (f'Are the {svc_plural} listed here real, verified businesses?',
         f'Each listing is a specific named business with a verified phone number and website — not a generic call center or lead-routing service. CallNowService allows a maximum of five providers per service per city.'),
        (f'What if a listed {svc_lower} in {city_name} doesn\'t answer?',
         f'Try the next listed provider — up to five approved {svc_plural} are shown for {city_name}, {state_abbr} so you have alternatives if the first business is unavailable.'),
        (f'Does CallNowService perform the {svc_lower} work itself?',
         f'No. CallNowService is a directory that connects you directly with independent local {svc_plural}. The businesses listed handle the actual service call.'),
    ]
    html_parts = []
    schema_items = []
    for q, a in qa:
        html_parts.append(f'<details class="faq-item"><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>')
        schema_items.append({
            "@type": "Question",
            "name": q,
            "acceptedAnswer": {"@type": "Answer", "text": a}
        })
    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": schema_items
    }
    return '\n      '.join(html_parts), json.dumps(schema, indent=2)


for state_key, state_info in data["states"].items():
    state_abbr = state_info["abbr"]
    for city_slug, city in state_info["cities"].items():
        for svc in services:
            svc_id = svc['id']
            svc_name = svc['name']
            svc_plural = svc.get('plural', svc_name.lower() + 's')
            other = [s for s in services if s['id'] != svc_id]
            alt_links = '\n      '.join(f'<a href="/{state_key}/{city_slug}/{s["id"]}/" class="alt-link">{s["name"]}</a>' for s in other)
            svc_opts = svc_options.replace(f'value="{svc_id}"', f'value="{svc_id}" selected')
            tip_html = '\n      '.join(f'<li>{t}</li>' for t in tips.get(svc_id, ['Emergency service needed']))

            result_count_static, provider_list_static = render_static_providers(city_slug, svc_id, svc_name)
            faq_html, faq_schema = render_faq(svc_name, svc_plural, city['name'], state_abbr)

            html_out = template
            html_out = html_out.replace('__TITLE__', f'Emergency {svc_name} in {city["name"]}, {state_abbr} | CallNowService')
            html_out = html_out.replace('__META_DESC__', f'Find approved emergency {svc_name.lower()} serving {city["name"]}, {state_abbr}. View up to five provider listings and contact businesses directly by phone, website, or booking page.')
            html_out = html_out.replace('__STATE_NAME__', state_info["name"])
            html_out = html_out.replace('__STATE_SLUG__', state_key)
            html_out = html_out.replace('__STATE_ABBR__', state_abbr)
            html_out = html_out.replace('__CITY_NAME__', city['name'])
            html_out = html_out.replace('__CITY_SLUG__', city_slug)
            html_out = html_out.replace('__SERVICE_NAME__', svc_name)
            html_out = html_out.replace('__SERVICE_SLUG__', svc_id)
            html_out = html_out.replace('__SERVICE_PLURAL__', svc_plural)
            html_out = html_out.replace('__SERVICE_OPTIONS__', svc_opts)
            html_out = html_out.replace('__ALTERNATE_LINKS__', alt_links)
            html_out = html_out.replace('__EMERGENCY_TIPS__', tip_html)
            html_out = html_out.replace('__RESULT_COUNT_STATIC__', result_count_static)
            html_out = html_out.replace('__PROVIDER_LIST_STATIC__', provider_list_static)
            html_out = html_out.replace('__FAQ_HTML__', faq_html)
            html_out = html_out.replace('__FAQ_SCHEMA__', faq_schema)

            dir_path = os.path.join(state_key, city_slug, svc_id)
            os.makedirs(dir_path, exist_ok=True)
            with open(os.path.join(dir_path, 'index.html'), 'w', encoding='utf-8', newline='\n') as f:
                f.write(html_out)

print(f'Done! {len(data["states"])} states regenerated.')
print(f'Provider lists are now server-rendered at build time (crawlable without JS) and refreshed live via providers.json fetch.')
