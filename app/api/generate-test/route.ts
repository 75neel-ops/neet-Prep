import { NextResponse } from 'next/server';
import { generateJson } from '@/lib/ai';

export async function POST(request:Request) {
  try {
    const body=await request.json();
    const subject=String(body.subject||'Physics');
    const chapter=String(body.chapter||'General');
    const count=Math.min(50,Math.max(1,Number(body.count)||10));
    const prompt=`Generate ${count} fresh multiple-choice NEET practice questions for the subject "${subject}" and chapter "${chapter}". Follow the current NCERT syllabus. Use four plausible options. Avoid repeating known question formulations and return no unsupported claims. Include fields: question, options (array), answer (exactly matching one options string), explanation, source (specific NCERT class and chapter/topic if known). Return JSON as {"questions":[...]}. Mark difficult or uncertain topics explicitly by preferring the standard NCERT definition.`;
    const data=await generateJson(prompt);
    const questions=(data.questions||[]).filter((q:any)=>q?.question&&Array.isArray(q.options)&&q.options.length===4&&q.options.includes(q.answer));
    if(!questions.length) throw new Error('The AI returned no usable questions');
    return NextResponse.json({questions,generated:true});
  } catch(error:any) {
    return NextResponse.json({error:error.message||'Question generation failed'}, {status:500});
  }
}
