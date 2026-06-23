// Vercel serverless function — provider signup intake
// POST to /api/signup — commits signup to signups.json in GitHub repo

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const data = req.body;
  const now = new Date().toISOString();
  
  const required = ['name', 'contact', 'email', 'phone', 'service', 'city', 'plan'];
  for (const field of required) {
    if (!data[field]) {
      return res.status(400).json({ error: `Missing required field: ${field}` });
    }
  }

  const signup = {
    company: data.name,
    contact: data.contact,
    email: data.email,
    phone: data.phone,
    website: data.website || '',
    service: data.service,
    city: data.city,
    plan: data.plan,
    extra_cities: data.extra_cities || '',
    extra_services: data.extra_services || '',
    gbp: data.gbp || '',
    routing: data.routing || '',
    desc: data.desc || '',
    submitted_at: now,
    status: 'pending'
  };

  const token = process.env.GITHUB_TOKEN;
  if (!token) {
    // Fallback: return success so form doesn't error, signup stored in localStorage client-side
    return res.status(200).json({ 
      status: 'received',
      message: 'Thank you! We will review your business and reach out within 24 hours. Or skip the wait — pay now: paypal.me/CallNowService',
      warning: 'Backend storage unavailable — signup saved client-side only'
    });
  }

  try {
    const repo = 'autho369-code/emergency-near-me';
    const path = 'signups.json';
    
    // Get current signups.json (with SHA for update)
    let existingSignups = [];
    let sha = null;
    try {
      const getRes = await fetch(`https://api.github.com/repos/${repo}/contents/${path}`, {
        headers: { Authorization: `Bearer ${token}`, 'Accept': 'application/vnd.github.v3+json' }
      });
      if (getRes.ok) {
        const fileData = await getRes.json();
        existingSignups = JSON.parse(Buffer.from(fileData.content, 'base64').toString('utf-8'));
        sha = fileData.sha;
      }
    } catch (e) {
      // File doesn't exist yet — start fresh
    }
    
    existingSignups.push(signup);
    
    const content = Buffer.from(JSON.stringify(existingSignups, null, 2)).toString('base64');
    const body = {
      message: `Signup: ${signup.company} — ${signup.service} in ${signup.city}`,
      content: content
    };
    if (sha) body.sha = sha;
    
    const putRes = await fetch(`https://api.github.com/repos/${repo}/contents/${path}`, {
      method: 'PUT',
      headers: { Authorization: `Bearer ${token}`, 'Accept': 'application/vnd.github.v3+json' },
      body: JSON.stringify(body)
    });
    
    if (!putRes.ok) {
      const err = await putRes.text();
      console.error('GitHub API error:', err);
    }
  } catch (e) {
    console.error('Signup storage error:', e);
  }

  return res.status(200).json({ 
    status: 'received', 
    message: 'Thank you! We will review your business and reach out within 24 hours. Or skip the wait — pay now: paypal.me/CallNowService',
    service: signup.service,
    city: signup.city,
    plan: signup.plan
  });
}
