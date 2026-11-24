'use client';

import { useEffect, useState } from 'react';
import './globals.css';

const subjects = [
  { name:'Physics', icon:'ƒ', color:'#ebe7ff', progress:68 },
  { name:'Chemistry', icon:'⚗', color:'#e1f4ef', progress:54 },
  { name:'Botany', icon:'❋', color:'#edf4dd', progress:72 },
  { name:'Zoology', icon:'◉', color:'#fee8df', progress:61 },
];

type Question = { question:string; options:string[]; answer:string; explanation:string; source:string };

export default function Home() {
  const [tab,setTab] = useState('Dashboard');
  const [subject,setSubject] = useState('Physics');
  const [chapter,setChapter] = useState('Electrostatics');
  const [count,setCount] = useState('10');
  const [minutes,setMinutes] = useState('30');
  const [questions,setQuestions] = useState<Question[]>([]);
  const [index,setIndex] = useState(0);
  const [selected,setSelected] = useState<number|null>(null);
  const [seconds,setSeconds] = useState(0);
  const [loading,setLoading] = useState(false);
  const [error,setError] = useState('');

  useEffect(() => {
    if (!questions.length || seconds <= 0) return;
    const timer=setInterval(()=>setSeconds(s=>Math.max(0,s-1)),1000);
    return()=>clearInterval(timer);
  },[questions.length,seconds]);

  async function startTest() {
    setLoading(true);setError('');setQuestions([]);setIndex(0);setSelected(null);
    try {
      const res=await fetch('/api/generate-test',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({subject,chapter,count:Number(count),minutes:Number(minutes)})});
      const data=await res.json();
      if(!res.ok) throw new Error(data.error || 'Could not generate questions');
      setQuestions(data.questions);setSeconds(Number(minutes)*60);
    } catch(e:any){ setError(e.message); }
    finally { setLoading(false); }
  }

  const q=questions[index];
  const nav=['Dashboard','Study','Practice','Mock tests','NCERT Q&A','Resources','Rank predictor'];

  return <div className="shell">
    <aside className="sidebar">
      <div className="brand"><div className="brand-mark">N</div>NEETPrep</div>
      <nav className="nav">{nav.map((item,i)=><button key={item} className={tab===item?'active':''} onClick={()=>setTab(item)}><span>{['▦','▣','✎','◷','?','⌁','▲'][i]}</span><span>{item}</span></button>)}</nav>
      <div className="profile"><div className="avatar">NS</div><div><b>NEET Aspirant</b><small>Class 12 • 2027</small></div></div>
    </aside>
    <main className="main">
      <header className="topbar"><div className="search">⌕ &nbsp; Search chapters, topics or questions</div><div><button className="icon-button">◉</button><button className="icon-button">♢</button></div></header>
      <div className="content">
        <div className="eyebrow">Monday, 24 November</div>
        <h1>{tab}</h1>
        {tab==='Dashboard' && <>
          <section className="hero"><div><span className="eyebrow">Continue learning</span><h2>Electrostatic Potential & Capacitance</h2><p>Master NCERT concepts with AI practice that adapts to your chapter and difficulty.</p><button className="primary" onClick={()=>{setTab('Practice');setChapter('Electrostatic Potential and Capacitance')}}>Continue chapter →</button></div><div className="hero-art"><div className="orb">⚡</div></div></section>
          <div className="section-head"><h2>Your subjects</h2><button className="icon-button">•••</button></div>
          <div className="cards">{subjects.map(s=><article className="card" key={s.name}><div className="subject"><div className="subject-icon" style={{background:s.color}}>{s.icon}</div><b>{s.progress}%</b></div><h3>{s.name}</h3><p>NCERT-aligned chapter practice</p><div className="progress"><div style={{width:`${s.progress}%`}}/></div></article>)}</div>
        </>}
        {(tab==='Practice'||tab==='Mock tests') && <>
          <div className="test-grid"><section className="panel">
            <div className="test-head"><b>{q?`Question ${index+1} of ${questions.length}`:'Generate a practice test'}</b>{questions.length>0&&<span className="timer">◷ {Math.floor(seconds/60)}:{String(seconds%60).padStart(2,'0')}</span>}</div>
            {!questions.length ? <><p>AI creates fresh questions every time. They are practice questions, not claimed past NEET papers.</p><div className="controls">
              <label>Subject<select value={subject} onChange={e=>setSubject(e.target.value)}><option>Physics</option><option>Chemistry</option><option>Biology</option></select></label>
              <label>Chapter<select value={chapter} onChange={e=>setChapter(e.target.value)}><option>Electrostatics</option><option>Human Physiology</option><option>Genetics</option><option>Organic Chemistry</option></select></label>
              <label>Questions<select value={count} onChange={e=>setCount(e.target.value)}><option>5</option><option>10</option><option>20</option><option>50</option></select></label>
              <label>Time<select value={minutes} onChange={e=>setMinutes(e.target.value)}><option>15</option><option>30</option><option>60</option><option>180</option></select></label>
            </div><button className="primary" disabled={loading} onClick={startTest}>{loading?'Generating…':'Generate fresh test'}</button>{error&&<p style={{color:'#c44',marginTop:12}}>{error}</p>}</> : <>
              <div className="question">{q.question}</div><div className="options">{q.options.map((o,i)=><button key={o} className={`option ${selected===i?(i===q.options.indexOf(q.answer)?'correct':'wrong'):''}`} onClick={()=>setSelected(i)}>{String.fromCharCode(65+i)}. &nbsp; {o}</button>)}</div>
              {selected!==null&&<div className="answer-box"><b>Explanation</b><br/> {q.explanation}<br/><small>NCERT alignment: {q.source}</small></div>}
              <div style={{display:'flex',justifyContent:'space-between',marginTop:18}}><button className="primary" disabled={index===0} onClick={()=>{setIndex(index-1);setSelected(null)}}>Previous</button><button className="primary" onClick={()=>{if(index<questions.length-1){setIndex(index+1);setSelected(null)}else setQuestions([])}}>{index<questions.length-1?'Next':'Finish'}</button></div>
            </>}
          </section><aside className="panel"><h3>Today’s goal</h3><div className="rank">12 / 30</div><p>questions completed</p><div className="progress"><div style={{width:'40%',background:'var(--purple)'}}/></div><h3 style={{marginTop:24}}>Rank estimate</h3><div class="notice">All India Rank is an estimate and should not be treated as an official result.</div></aside></div>
        </>}
        {['Study','NCERT Q&A','Resources','Rank predictor'].includes(tab)&&<section className="panel"><h2>{tab}</h2><p>This module is ready for the next implementation milestone. Configure your AI API key to enable chapter generation and NCERT-guided answers.</p><div className="notice">Always verify AI-generated guidance against the latest official NCERT and NTA syllabus.</div></section>}
      </div>
    </main>
  </div>;
}
