import json
from datetime import datetime, timedelta

with open('providers.json') as f:
    data = json.load(f)

vendors = data['aurora-il']['plumber']
trial_start = datetime.now().strftime('%Y-%m-%dT%H:%M')
trial_exp = (datetime.now() + timedelta(hours=72)).strftime('%Y-%m-%dT%H:%M')

providers = [
    {
        'provider_name': 'Jim Wagner Plumbing, Inc.',
        'provider_phone': '(630) 577-9241',
        'provider_website': 'https://www.jimwagnerplumbing.com',
        'notes': '60+ yrs, 3rd-gen, flat-rate pricing, licensed #058-167743, 1000+ reviews'
    },
    {
        'provider_name': 'Plumb It Best',
        'provider_phone': '(630) 544-7162',
        'provider_website': 'https://www.plumbitbest.com',
        'notes': 'Veteran-owned, emergency services, serves Fox Valley, honest pricing'
    },
    {
        'provider_name': 'Four Seasons Plumbing',
        'provider_phone': '(888) 835-7451',
        'provider_website': 'https://www.fourseasonsheatingcooling.com',
        'notes': '54 yrs, 24/7/365, BBB Torch Award, 27600+ reviews, written warranty'
    },
    {
        'provider_name': 'Andersen Plumbing and Heating',
        'provider_phone': '(630) 937-3837',
        'provider_website': 'https://andersenph.com',
        'notes': '24/7 emergency, licensed, financing available, same-day service'
    },
    {
        'provider_name': "Big Daddy's Plumbing",
        'provider_phone': '(888) 897-3176',
        'provider_website': 'https://www.bigdaddysplumbing.com',
        'notes': '24/7 emergency, licensed and insured, trenchless pipe lining, local experts'
    }
]

for i, p in enumerate(providers):
    vendors[i]['status'] = 'trial_created'
    vendors[i]['provider_name'] = p['provider_name']
    vendors[i]['provider_phone'] = p['provider_phone']
    vendors[i]['provider_website'] = p['provider_website']
    vendors[i]['notes'] = p['notes']
    vendors[i]['trial_started'] = trial_start
    vendors[i]['trial_expires'] = trial_exp

# Update meta
data['_meta']['filled'] = data['_meta'].get('filled', 0) + 5
data['_meta']['searching'] = data['_meta'].get('searching', 0) - 5
data['_meta']['found'] = data['_meta'].get('found', 0) + 5
data['_meta']['trial_providers'] = data['_meta'].get('trial_providers', 0) + 5
data['_meta']['updated'] = datetime.now().strftime('%Y-%m-%d')

with open('providers.json', 'w') as f:
    json.dump(data, f, indent=2)

print('OK: 5 providers added to aurora-il/plumber')
print(f'Trial started: {trial_start}')
print(f'Trial expires: {trial_exp}')
for p in providers:
    print(f'  - {p["provider_name"]} | {p["provider_phone"]} | {p["provider_website"]}')
