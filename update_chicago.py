import json

with open('providers.json', 'r') as f:
    data = json.load(f)

chicago = data['chicago']

# ---- PLUMBERS (slots 2, 3, 4) ----
plumbers = chicago['plumber']
updates = {
    2: {
        "provider_name": "Chicago Plumbing Experts",
        "provider_phone": "+17087752566",
        "provider_website": "https://www.chicagoplumbingexperts.com",
        "notes": "24/7 emergency, 2155 W Belmont Ave Chicago, licensed & insured, upfront pricing"
    },
    3: {
        "provider_name": "Good Guys 24/7 Emergency Plumbers",
        "provider_phone": "+17086831006",
        "provider_website": "https://goodguys247.com",
        "notes": "24/7 service since 1995, licensed bonded insured, free estimates"
    },
    4: {
        "provider_name": "Mike's Chicago Plumbing",
        "provider_phone": "+17738758833",
        "provider_website": "https://mikesplumbingchicago.com",
        "notes": "24/7 emergency, since 1997, 45-min avg response, 10-yr labor warranty"
    }
}
for slot_id, info in updates.items():
    plumbers[slot_id]['status'] = 'found'
    for k, v in info.items():
        plumbers[slot_id][k] = v

# ---- ELECTRICIANS (slots 1, 2, 3, 4) ----
electricians = chicago['electrician']
e_updates = {
    1: {
        "provider_name": "Mr. Mighty Electric",
        "provider_phone": "+17734067500",
        "provider_website": "https://www.mrmightyelectric.com",
        "notes": "24/7 emergency, 30+ yrs, 700+ 5-star reviews, flat-rate pricing, BBB accredited"
    },
    2: {
        "provider_name": "All Ed Electric",
        "provider_phone": "+17738425536",
        "provider_website": "https://www.alledelectricil.com",
        "notes": "24/7 emergency, licensed & insured, EV charger install, serves Chicago/Skokie/Evanston"
    },
    3: {
        "provider_name": "Jimco Electric",
        "provider_phone": "+17085840557",
        "provider_website": "https://www.jimcoelectric.com",
        "notes": "24/7 emergency, 25+ yrs, same rate nights/weekends, no after-hours surcharge"
    },
    4: {
        "provider_name": "Loboz Electric",
        "provider_phone": "+17086320438",
        "provider_website": "https://www.lobozelectrical.com",
        "notes": "Emergency service, 10+ yrs, licensed & insured, free estimates, Downtown Chicago"
    }
}
for slot_id, info in e_updates.items():
    electricians[slot_id]['status'] = 'found'
    for k, v in info.items():
        electricians[slot_id][k] = v

# ---- HVAC (slots 1, 2, 3, 4) ----
hvac = chicago['hvac']
h_updates = {
    1: {
        "provider_name": "Four Seasons Heating, Air Conditioning, Plumbing & Electric",
        "provider_phone": "+18664442404",
        "provider_website": "https://www.fourseasonsheatingcooling.com",
        "notes": "24/7 emergency, since 1971, Lennox Premier Dealer, 27,600+ reviews, BBB Torch Award"
    },
    2: {
        "provider_name": "Browns Heating & Cooling",
        "provider_phone": "+17085368134",
        "provider_website": "https://brownshvac.net",
        "notes": "24/7 emergency HVAC, EPA-certified, 4.9 Google rating, furnace/AC/heat pump repair"
    },
    3: {
        "provider_name": "Bean'z Heating & Cooling",
        "provider_phone": "+13125936334",
        "provider_website": "https://beanzheatingandcooling.com",
        "notes": "Same-day AC repair, 24/7 emergency, 5.0 Google rating, South Side local experts"
    },
    4: {
        "provider_name": "Air-Rite Heating & Cooling",
        "provider_phone": "+16309668100",
        "provider_website": "https://www.air-rite.com",
        "notes": "24/7/365 emergency, since 1959, serves Greater Chicagoland, coupons & financing"
    }
}
for slot_id, info in h_updates.items():
    hvac[slot_id]['status'] = 'found'
    for k, v in info.items():
        hvac[slot_id][k] = v

# Write back
with open('providers.json', 'w') as f:
    json.dump(data, f, indent=2)

print("Done! Updated:")
print("  Plumber slots 2,3,4 -> found")
print("  Electrician slots 1,2,3,4 -> found")
print("  HVAC slots 1,2,3,4 -> found")
print("  Total: 11 providers updated")

# Verify
with open('providers.json', 'r') as f:
    verify = json.load(f)
vc = verify['chicago']
for svc_name, svc_list in [('plumber', vc['plumber']), ('electrician', vc['electrician']), ('hvac', vc['hvac'])]:
    found = sum(1 for s in svc_list if s.get('status') == 'found')
    searching = sum(1 for s in svc_list if s.get('status') == 'searching')
    print(f"  {svc_name}: {found} found, {searching} searching")
