// Vercel serverless function — GET /api/geocode?q=<zip or city name>
// 5-digit input is resolved via zippopotam.us (free, no key) then snapped to the
// nearest known city; otherwise matched by name against data.json.
import { findCityByName, nearestCity } from './_geo.js';

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  const q = (req.query.q || '').toString().trim();
  if (!q) return res.status(400).json({ error: 'Missing query' });

  if (/^\d{5}$/.test(q)) {
    try {
      const r = await fetch(`https://api.zippopotam.us/us/${q}`);
      if (r.ok) {
        const zdata = await r.json();
        const place = zdata.places && zdata.places[0];
        if (place) {
          const lat = parseFloat(place.latitude);
          const lon = parseFloat(place.longitude);
          const result = nearestCity(lat, lon);
          if (result) return res.status(200).json(result);
        }
      }
    } catch (e) {
      // fall through to not-found below
    }
    return res.status(404).json({ error: 'ZIP not found' });
  }

  const result = findCityByName(q);
  if (!result) return res.status(404).json({ error: 'City not found' });
  return res.status(200).json(result);
}
