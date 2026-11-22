import React, { useEffect, useMemo, useState } from "react";
import {
  Activity, ArrowDown, ArrowRight, ArrowUpRight, BookOpen, BrainCircuit,
  Check, ChevronDown, Code2, Copy, Database, FileText, Filter, Globe2,
  Layers3, Menu, Network, Plus, Search, ShieldCheck, Sparkles, Trash2, X
} from "lucide-react";

const API_BASE_URL = (import.meta.env.VITE_API_URL || "").replace(/\/$/, "");
const apiUrl = (path) => `${API_BASE_URL}${path}`;

const categories = ["Computer Science", "Artificial Intelligence", "Science", "Mathematics", "Healthcare", "History", "Technology"];
const sqlExamples = {
  SELECT: {
    sql: "SELECT id, title, category\nFROM knowledge\nWHERE category = 'Computer Science'\nORDER BY created_at DESC;",
    explain: "SELECT retrieves records from a table. WHERE filters rows by a condition, and ORDER BY sorts the returned records."
  },
  INSERT: {
    sql: "INSERT INTO knowledge\n(title, content, category, source, tags)\nVALUES\n('Cloud Computing', 'Delivery of computing services over the internet.',\n 'Technology', 'Class notes', 'cloud, computing');",
    explain: "INSERT INTO adds a new row to the knowledge table. Each value corresponds to a column listed in the INSERT statement."
  },
  UPDATE: {
    sql: "UPDATE knowledge\nSET category = 'Technology'\nWHERE id = 3;",
    explain: "UPDATE changes existing records. The WHERE clause is essential: without it, every row in the table could be modified."
  },
  DELETE: {
    sql: "DELETE FROM knowledge\nWHERE id = 3;",
    explain: "DELETE removes matching rows. Always verify the WHERE condition first, and consider a transaction or backup for important data."
  }
};

function App() {
  const [stats, setStats] = useState({ total: "—", categories: "—", sources: "—" });
  const [records, setRecords] = useState([]);
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("");
  const [loading, setLoading] = useState(true);
  const [dbError, setDbError] = useState("");
  const [activeSql, setActiveSql] = useState("SELECT");
  const [modal, setModal] = useState(false);
  const [mobileNav, setMobileNav] = useState(false);
  const [toast, setToast] = useState("");
  const [form, setForm] = useState({ title: "", content: "", category: "", source: "", tags: "" });
  const [saving, setSaving] = useState(false);

  const notify = (message) => {
    setToast(message);
    window.setTimeout(() => setToast(""), 2600);
  };

  async function fetchStats() {
    try {
      const response = await fetch(apiUrl("/api/stats"));
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Could not load stats");
      setStats(data);
    } catch {
      setDbError("MySQL is not connected yet. Follow the README setup steps to start the database.");
    }
  }

  async function fetchRecords() {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (query.trim()) params.set("q", query.trim());
      if (category) params.set("category", category);
      const response = await fetch(apiUrl(`/api/knowledge?${params.toString()}`));
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Database unavailable");
      setRecords(data);
      setDbError("");
    } catch (error) {
      setRecords([]);
      setDbError(error.message || "Unable to connect to MySQL.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { fetchStats(); }, []);
  useEffect(() => {
    const timer = window.setTimeout(fetchRecords, 250);
    return () => window.clearTimeout(timer);
  }, [query, category]);

  async function addRecord(event) {
    event.preventDefault();
    setSaving(true);
    try {
      const response = await fetch(apiUrl("/api/knowledge"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form)
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Could not save record");
      setForm({ title: "", content: "", category: "", source: "", tags: "" });
      setModal(false);
      notify("Knowledge record saved successfully.");
      await fetchRecords();
      await fetchStats();
    } catch (error) {
      notify(error.message);
    } finally {
      setSaving(false);
    }
  }

  async function deleteRecord(id) {
    if (!window.confirm("Delete this knowledge record?")) return;
    try {
      const response = await fetch(apiUrl(`/api/knowledge/${id}`), { method: "DELETE" });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Could not delete record");
      notify("Record deleted.");
      await fetchRecords();
      await fetchStats();
    } catch (error) {
      notify(error.message);
    }
  }

  async function copySql() {
    try {
      await navigator.clipboard.writeText(sqlExamples[activeSql].sql);
      notify("SQL query copied.");
    } catch {
      notify("Clipboard access is unavailable in this browser.");
    }
  }

  const navLinks = ["About", "Architecture", "Database", "Explorer", "SQL Lab"];
  const activeExample = sqlExamples[activeSql];

  return (
    <>
      <div className="ambient ambient-a" /><div className="ambient ambient-b" />
      <header className="topbar">
        <a className="brand" href="#home"><span className="brand-mark">U</span><span>UKD<span className="brand-dot">.</span></span></a>
        <nav className={mobileNav ? "nav-open" : ""}>
          {navLinks.map((item) => <a key={item} href={`#${item.toLowerCase().replace(" ", "-")}`} onClick={() => setMobileNav(false)}>{item}</a>)}
        </nav>
        <a className="nav-cta" href="#explorer">Explore knowledge <ArrowUpRight size={14} /></a>
        <button className="menu-btn" onClick={() => setMobileNav(!mobileNav)} aria-label="Toggle menu">{mobileNav ? <X /> : <Menu />}</button>
      </header>

      <main>
        <section className="hero section" id="home">
          <div className="hero-copy">
            <div className="eyebrow"><span className="pulse" /> DATABASE MANAGEMENT SYSTEM · PROJECT</div>
            <h1>Knowledge has<br />no <span className="gradient-text">boundaries.</span></h1>
            <p className="hero-lead">One intelligent place to collect, connect, organize and discover information across every domain.</p>
            <div className="hero-actions"><a className="btn primary" href="#explorer">Explore the database <ArrowRight size={15} /></a><a className="btn secondary" href="#architecture">View architecture</a></div>
            <div className="hero-meta"><div className="avatar-stack"><i>⌘</i><i>⌬</i><i>◈</i></div><span>Structured knowledge. Simple discovery.</span></div>
          </div>
          <div className="hero-visual" aria-label="Connected knowledge network illustration">
            <div className="orbit orbit-one" /><div className="orbit orbit-two" />
            <div className="core"><div className="core-inner">UKD<span>CORE</span></div></div>
            <div className="node node-top"><b><BrainCircuit size={17}/></b><span>Intelligence</span></div>
            <div className="node node-right"><b><Database size={17}/></b><span>Structured data</span></div>
            <div className="node node-bottom"><b>∞</b><span>Knowledge</span></div>
            <div className="node node-left"><b><Search size={17}/></b><span>Discovery</span></div>
          </div>
          <div className="hero-bottom"><span>01 / A UNIFIED KNOWLEDGE SPACE</span><span>SCROLL TO EXPLORE ↓</span></div>
        </section>

        <section className="stats-strip">
          <div><strong>{stats.total}</strong><span>Knowledge records</span></div>
          <div><strong>{stats.categories}</strong><span>Knowledge categories</span></div>
          <div><strong>{stats.sources}</strong><span>Information sources</span></div>
          <div><strong>24/7</strong><span>Knowledge access</span></div>
        </section>

        <section className="section content-section" id="about">
          <SectionHeading number="01" title={<>What is <span className="gradient-text">UKD?</span></>} description="A centralized knowledge platform designed to make information easier to store, manage, relate and retrieve." />
          <div className="about-grid">
            <article className="feature-card large-card"><div className="card-icon"><Network /></div><div className="card-kicker">THE BIG IDEA</div><h3>From scattered data<br />to connected knowledge.</h3><p>Information often lives in separate files, systems and databases. UKD brings knowledge into a unified structure, making it easier to search and understand.</p><div className="mini-flow"><span>Sources</span><b>→</b><span>UKD</span><b>→</b><span>Insights</span></div></article>
            <Feature icon={<Layers3 />} title="Organized" text="Classify information by topic, source and tags." />
            <Feature icon={<Search />} title="Discoverable" text="Find relevant records using search and filters." />
            <Feature icon={<Network />} title="Connected" text="Build relationships between concepts and domains." />
            <Feature icon={<ShieldCheck />} title="Consistent" text="Use structured tables and constraints to maintain data quality." />
          </div>
        </section>

        <section className="section architecture-section" id="architecture">
          <SectionHeading number="02" title={<>How the system <span className="gradient-text">works.</span></>} description="A layered architecture separates the user interface, application logic and persistent data storage." />
          <div className="architecture">
            <ArchLayer label="01 · INPUT LAYER" items={["Documents", "Web sources", "User entries", "External APIs"]} />
            <ArchArrow text="collect & validate" />
            <ArchLayer label="02 · APPLICATION LAYER" items={["React interface", "Flask / Python", "Validation", "Search & filtering"]} />
            <ArchArrow text="SQL queries" />
            <div className="arch-layer data-layer"><label>03 · DATABASE LAYER</label><div className="db-cylinder"><b>MySQL</b><span>Knowledge · Categories · Sources</span></div></div>
            <ArchArrow text="retrieve results" />
            <ArchLayer label="04 · OUTPUT LAYER" items={["Search results", "Knowledge cards", "Statistics", "Insights"]} />
          </div>
          <div className="tech-row"><span>BUILT WITH</span>{["React", "HTML5", "CSS3", "JavaScript", "Python Flask", "MySQL"].map(t => <b key={t}>{t}</b>)}</div>
        </section>

        <section className="section content-section" id="database">
          <SectionHeading number="03" title={<>Structured at the <span className="gradient-text">core.</span></>} description="A relational database stores knowledge records and organizes them with categories, attributes and constraints." />
          <div className="schema-grid">
            <SchemaCard number="TABLE 01" name="knowledge" fields={[["🔑 id","INT · PRIMARY KEY"],["title","VARCHAR(180)"],["content","TEXT"],["category","VARCHAR(80)"],["source","VARCHAR(180)"],["tags","VARCHAR(255)"],["created_at","TIMESTAMP"]]} />
            <div className="relation"><span>categories</span><div className="relation-line">1 ───────── ∞</div><span>knowledge</span><small>One category can contain many knowledge records.</small></div>
            <SchemaCard number="TABLE 02" name="categories" fields={[["🔑 id","INT · PRIMARY KEY"],["name","VARCHAR(80) · UNIQUE"],["description","VARCHAR(255)"]]} note="Category names group knowledge records into meaningful domains." />
          </div>
          <div className="normalization-note"><Check /><div><b>Database design principles</b><p>Primary keys provide unique identification. Indexes improve lookup speed. Categories are maintained separately to reduce repeated category descriptions and support consistent classification.</p></div></div>
        </section>

        <section className="section explorer-section" id="explorer">
          <SectionHeading number="04" title={<>Knowledge <span className="gradient-text">Explorer.</span></>} description="Search the sample database, filter by category, and add new knowledge records." />
          <div className="explorer-toolbar">
            <div className="search-box"><Search size={19}/><input value={query} onChange={e => setQuery(e.target.value)} placeholder="Search concepts, topics or keywords..." /><kbd>↵</kbd></div>
            <select value={category} onChange={e => setCategory(e.target.value)}><option value="">All categories</option>{categories.map(c => <option key={c}>{c}</option>)}</select>
            <button className="btn primary" onClick={() => setModal(true)}><Plus size={16}/> Add knowledge</button>
          </div>
          <div className="results-line"><span>{loading ? "Searching records..." : `${records.length} record${records.length === 1 ? "" : "s"} found`}</span><span className="live-indicator"><i/> DATABASE SEARCH</span></div>
          {dbError && <div className="db-alert"><Activity size={17}/><span>{dbError}</span></div>}
          <div className="knowledge-grid">
            {!loading && records.map(record => <article className="knowledge-card" key={record.id}>
              <span className="category">{record.category}</span><h3>{record.title}</h3><p>{record.content}</p>
              <footer><span>{record.source || "UKD"} · #{record.id}</span><button className="delete-record" onClick={() => deleteRecord(record.id)} title="Delete record"><Trash2 size={14}/> Delete</button></footer>
            </article>)}
            {loading && <div className="loading-card">Loading knowledge records...</div>}
            {!loading && !records.length && !dbError && <div className="loading-card">No matching records. Try another search or add a new entry.</div>}
          </div>
        </section>

        <section className="section sql-section" id="sql-lab">
          <SectionHeading number="05" title={<>SQL <span className="gradient-text">playground.</span></>} description="Explore the core SQL operations used to manage data in a relational database." />
          <div className="sql-layout">
            <div className="sql-tabs">{Object.keys(sqlExamples).map(key => <button key={key} className={activeSql === key ? "sql-tab active" : "sql-tab"} onClick={() => setActiveSql(key)}>{key}</button>)}</div>
            <div className="sql-editor"><div className="editor-top"><span className="window-dots"><i/><i/><i/></span><small>MYSQL · QUERY EXAMPLE</small><button onClick={copySql}><Copy size={12}/> Copy query</button></div><pre><code>{activeExample.sql}</code></pre><div className="sql-explain">{activeExample.explain}</div></div>
          </div>
          <p className="sql-warning">These are educational SQL examples. Run modification queries only on test data and use a WHERE clause to target the intended records.</p>
        </section>

        <section className="section benefits-section" id="benefits">
          <SectionHeading number="06" title={<>One system. <span className="gradient-text">Many possibilities.</span></>} description="A unified knowledge layer can support information discovery across different fields." />
          <div className="usecase-grid">
            <UseCase icon={<BookOpen/>} title="Education" text="Organize notes, concepts, learning resources and study material."/>
            <UseCase icon={<ShieldCheck/>} title="Healthcare" text="Structure approved medical references and research information."/>
            <UseCase icon={<Sparkles/>} title="Research" text="Connect papers, findings, authors and related topics."/>
            <UseCase icon={<Globe2/>} title="Business" text="Centralize policies, process documentation and product knowledge."/>
          </div>
          <div className="conclusion"><div className="eyebrow">07 — CONCLUSION</div><h2>Make knowledge<br/><span className="gradient-text">work together.</span></h2><p>Universal Knowledge Database demonstrates how DBMS concepts—structured storage, relationships, constraints, indexing and SQL operations—can create a useful foundation for unified knowledge management.</p><a href="#home" className="btn secondary">Back to top ↑</a></div>
        </section>
      </main>

      <footer className="site-footer"><a className="brand" href="#home"><span className="brand-mark">U</span><span>UKD<span className="brand-dot">.</span></span></a><span>UNIVERSAL KNOWLEDGE DATABASE · DBMS PROJECT</span><span>React · Python · MySQL</span></footer>

      {modal && <div className="modal-backdrop" onMouseDown={e => e.target === e.currentTarget && setModal(false)}>
        <div className="modal"><div className="modal-head"><div><div className="eyebrow">CONTRIBUTE TO UKD</div><h3>Add knowledge</h3></div><button className="close-btn" onClick={() => setModal(false)}><X/></button></div>
          <form onSubmit={addRecord}>
            <label>Title<input required maxLength="180" value={form.title} onChange={e => setForm({...form,title:e.target.value})} placeholder="e.g. What is cloud computing?"/></label>
            <label>Category<select required value={form.category} onChange={e => setForm({...form,category:e.target.value})}><option value="">Choose a category</option>{categories.map(c=><option key={c}>{c}</option>)}</select></label>
            <label>Knowledge / Description<textarea required rows="4" value={form.content} onChange={e => setForm({...form,content:e.target.value})} placeholder="Write a clear explanation..."/></label>
            <label>Source<input value={form.source} onChange={e => setForm({...form,source:e.target.value})} placeholder="Book, website, class notes..."/></label>
            <label>Tags<input value={form.tags} onChange={e => setForm({...form,tags:e.target.value})} placeholder="database, SQL, learning"/></label>
            <button className="btn primary full" disabled={saving}>{saving ? "Saving..." : "Save knowledge record →"}</button>
          </form>
        </div>
      </div>}
      {toast && <div className="toast"><Check size={15}/>{toast}</div>}
    </>
  );
}

function SectionHeading({number,title,description}) {
  return <div className="section-heading"><div><div className="eyebrow">{number} — PROJECT OVERVIEW</div><h2>{title}</h2></div><p>{description}</p></div>;
}
function Feature({icon,title,text}) { return <article className="feature-card"><div className="card-icon">{icon}</div><h3>{title}</h3><p>{text}</p></article>; }
function ArchLayer({label,items}) { return <div className="arch-layer"><label>{label}</label><div className="arch-items">{items.map(x=><span key={x}>{x}</span>)}</div></div>; }
function ArchArrow({text}) { return <div className="arch-arrow"><ArrowDown size={17}/><small>{text}</small></div>; }
function SchemaCard({number,name,fields,note}) { return <div className="schema-card"><div className="schema-head"><span>{number}</span><b>{name}</b></div>{fields.map(([a,b])=><div className={`schema-row ${a.includes("🔑")?"pk":""}`} key={a}><span>{a}</span><small>{b}</small></div>)}{note&&<div className="schema-note">{note}</div>}</div>; }
function UseCase({icon,title,text}) { return <div className="usecase"><span>{icon}</span><b>{title}</b><p>{text}</p></div>; }

export default App;