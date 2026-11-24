export const runtime='nodejs';

type Provider='openai'|'gemini';

function cleanJson(text:string) {
  const start=text.indexOf('{');
  const array=text.indexOf('[');
  const beginning=start>=0&&(array<0||start<array)?start:array;
  if(beginning<0) throw new Error('The AI returned no valid JSON');
  let candidate=text.slice(beginning);
  candidate=candidate.replace(/```json|```/g,'').trim();
  return JSON.parse(candidate);
}

async function openAi(prompt:string) {
  const apiKey=process.env.OPENAI_API_KEY;
  if(!apiKey) throw new Error('OPENAI_API_KEY is not configured');
  const res=await fetch('https://api.openai.com/v1/chat/completions',{method:'POST',headers:{'Authorization':`Bearer ${apiKey}`,'Content-Type':'application/json'},body:JSON.stringify({model:process.env.OPENAI_MODEL||'gpt-4o-mini',messages:[{role:'system',content:'You generate valid JSON only. Never claim generated practice questions are real exam questions.'},{role:'user',content:prompt}],response_format:{type:'json_object'},temperature:.8})});
  if(!res.ok) throw new Error(`OpenAI request failed: ${await res.text()}`);
  const data=await res.json();
  return cleanJson(data.choices[0].message.content);
}

async function gemini(prompt:string) {
  const apiKey=process.env.GEMINI_API_KEY;
  if(!apiKey) throw new Error('GEMINI_API_KEY is not configured');
  const model=process.env.GEMINI_MODEL||'gemini-2.0-flash';
  const res=await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({contents:[{parts:[{text:`Return valid JSON only. ${prompt}`}]}],generationConfig:{temperature:.8,responseMimeType:'application/json'}})});
  if(!res.ok) throw new Error(`Gemini request failed: ${await res.text()}`);
  const data=await res.json();
  return cleanJson(data.candidates[0].content.parts[0].text);
}

export async function generateJson(prompt:string) {
  const provider=(process.env.AI_PROVIDER||'openai').toLowerCase() as Provider;
  return provider==='gemini'?gemini(prompt):openAi(prompt);
}
