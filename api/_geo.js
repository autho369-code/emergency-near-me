// Shared geo helpers for geocode.js / reverse-geocode.js
// Files prefixed with "_" are not exposed as routes by Vercel.
import fs from 'fs';
import path from 'path';

let cache = null;
export function loadData() {
  if (!cache) {
    const raw = fs.readFileSync(path.join(process.cwd(), 'data.json'), 'utf-8');
    cache = JSON.parse(raw);
  }
  return cache;
}

function toRad(deg) { return (deg * Math.PI) / 180; }

function haversineMiles(lat1, lon1, lat2, lon2) {
  const R = 3958.8;
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  const a = Math.sin(dLat / 2) ** 2 +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

export function nearestCity(lat, lng) {
  const data = loadData();
  let best = null;
  let bestDist = Infinity;
  for (const stateKey in data.states) {
    const state = data.states[stateKey];
    for (const cityKey in state.cities) {
      const city = state.cities[cityKey];
      if (typeof city.lat !== 'number' || typeof city.lng !== 'number') continue;
      const dist = haversineMiles(lat, lng, city.lat, city.lng);
      if (dist < bestDist) {
        bestDist = dist;
        best = { state: state.abbr, city: city.name, city_key: cityKey };
      }
    }
  }
  return best;
}

export function findCityByName(query) {
  const data = loadData();
  const q = query.trim().toLowerCase();
  const [namePart, statePart] = q.split(',').map((s) => s && s.trim());

  for (const stateKey in data.states) {
    const state = data.states[stateKey];
    if (statePart && state.abbr.toLowerCase() !== statePart && state.name.toLowerCase() !== statePart) continue;
    for (const cityKey in state.cities) {
      const city = state.cities[cityKey];
      if (city.name.toLowerCase() === namePart || cityKey === namePart.replace(/\s+/g, '-')) {
        return { state: state.abbr, city: city.name, city_key: cityKey };
      }
    }
  }
  for (const stateKey in data.states) {
    const state = data.states[stateKey];
    for (const cityKey in state.cities) {
      const city = state.cities[cityKey];
      if (city.name.toLowerCase().startsWith(namePart)) {
        return { state: state.abbr, city: city.name, city_key: cityKey };
      }
    }
  }
  return null;
}
