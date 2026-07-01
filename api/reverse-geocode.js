// Vercel serverless function — GET /api/reverse-geocode?lat=&lon=
// Returns the nearest known city to a lat/lon pair, using data.json's city coordinates.
import { nearestCity } from './_geo.js';

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  const lat = parseFloat(req.query.lat);
  const lon = parseFloat(req.query.lon);
  if (Number.isNaN(lat) || Number.isNaN(lon)) {
    return res.status(400).json({ error: 'Missing or invalid lat/lon' });
  }

  const result = nearestCity(lat, lon);
  if (!result) return res.status(404).json({ error: 'No city found' });
  return res.status(200).json(result);
}
