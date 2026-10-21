// Netlify invokes this event-only function after verifying a form submission.
// Gmail business notifications remain independent of acknowledgement delivery.
const FORM_ID = '6ad82b149706cb0d5e22ded0';
const FORM_NAME = 'elite-cleaning-quote';
const {renderReceipt}=require('../email-template.cjs');
exports.handler = async function (event) {
  if (process.env.CUSTOMER_EMAILS_ENABLED !== 'true' || (process.env.CONTEXT && process.env.CONTEXT !== 'production')) {
    return { statusCode: 200, body: 'Customer acknowledgements are not enabled.' };
  }
  let payload;
  try { payload = JSON.parse(event.body).payload; }
  catch { return { statusCode: 400, body: 'Invalid event.' }; }
  if (!payload || (payload.form_id !== FORM_ID && payload.form_name !== FORM_NAME)) {
    return { statusCode: 200, body: 'Not a cleaning request.' };
  }
  const data = payload.data || {};
  if (data.website || payload.spam === true) return { statusCode: 200, body: 'Skipped.' };
  const email = String(data.Email || data.email || '').trim();
  const id = String(payload.id || '');
  if (!/^[^\s@,;<>\r\n]+@[^\s@,;<>\r\n]+\.[^\s@,;<>\r\n]+$/.test(email) || email.length > 254 || !/^[a-zA-Z0-9_-]{1,100}$/.test(id)) {
    return { statusCode: 400, body: 'Invalid submission details.' };
  }
  if (!process.env.RESEND_API_KEY) {
    console.error('Customer acknowledgement: sending credential missing.');
    return { statusCode: 503, body: 'Email sender is not configured.' };
  }
  const consent = data['Marketing offers'] === 'Yes';
  const receipt = renderReceipt(consent);
  try {
    const response = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      signal: AbortSignal.timeout(8000),
      headers: {
        Authorization: 'Bearer ' + process.env.RESEND_API_KEY,
        'Content-Type': 'application/json',
        'Idempotency-Key': 'cleaning-request-' + id
      },
      body: JSON.stringify({
        from: 'Elite Clean Pro <hello@elitecleanpro.ca>',
        reply_to: 'hello@elitecleanpro.ca',
        to: [email],
        subject: 'Thank you for choosing Elite Clean Pro — request received',
        html: receipt.html,
        text: receipt.text
      })
    });
    if (!response.ok) {
      console.error('Customer acknowledgement provider status:', response.status);
      return { statusCode: 502, body: 'Acknowledgement delivery needs review.' };
    }
    console.info('Customer acknowledgement accepted by email provider.');
    return { statusCode: 200, body: 'Acknowledgement accepted.' };
  } catch {
    console.error('Customer acknowledgement: email provider unavailable.');
    return { statusCode: 502, body: 'Acknowledgement delivery needs review.' };
  }
};
