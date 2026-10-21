const assert=require('node:assert/strict');
const {handler}=require('../netlify/functions/submission-created');
const event=(changes={})=>({body:JSON.stringify({payload:{id:'receipt-test-123',form_id:'6ad82b149706cb0d5e22ded0',data:{Email:'receipt-test@example.com'},...changes}})});
(async()=>{
 let calls=[];global.fetch=async(url,options)=>{calls.push({url,...options});return {ok:true,status:200}};
 process.env.CONTEXT='deploy-preview';process.env.CUSTOMER_EMAILS_ENABLED='true';process.env.RESEND_API_KEY='test-only';
 assert.equal((await handler(event())).statusCode,200);assert.equal(calls.length,0);
 process.env.CONTEXT='production';process.env.CUSTOMER_EMAILS_ENABLED='false';await handler(event());assert.equal(calls.length,0);
 process.env.CUSTOMER_EMAILS_ENABLED='true';await handler(event({form_id:'another-form'}));assert.equal(calls.length,0);
 await handler(event({data:{Email:'receipt-test@example.com',website:'spam'}}));assert.equal(calls.length,0);
 assert.equal((await handler(event({data:{Email:'a@example.com,b@example.com'}}))).statusCode,400);assert.equal(calls.length,0);
 assert.equal((await handler(event())).statusCode,200);assert.equal(calls.length,1);
 const message=JSON.parse(calls[0].body);assert.deepEqual(message.to,['receipt-test@example.com']);assert.equal(message.reply_to,'hello@elitecleanpro.ca');assert.match(message.subject,/request received/);assert.match(message.text,/appointment is confirmed once/);assert.equal(calls[0].headers['Idempotency-Key'],'cleaning-request-receipt-test-123');
 await handler(event());assert.equal(calls[1].headers['Idempotency-Key'],calls[0].headers['Idempotency-Key']);
 global.fetch=async()=>({ok:false,status:429});assert.equal((await handler(event())).statusCode,502);
 delete process.env.RESEND_API_KEY;assert.equal((await handler(event())).statusCode,503);
 console.log('Customer acknowledgement checks passed: production-only gate, correct form/recipient, spam skip, stable duplicate key, honest message and provider-failure handling. No emails sent.');
})().catch(e=>{console.error(e);process.exitCode=1});
