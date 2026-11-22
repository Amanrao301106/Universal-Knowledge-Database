const $ = (s) => document.querySelector(s);
const esc = (v) => String(v ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const examples = {
 select: {sql:"SELECT id, title, category\nFROM knowledge\nWHERE category = 'Computer Science'\nORDER BY created_at DESC;", explain:"SELECT retrieves records from a table. WHERE filters rows by a condition, and ORDER BY sorts the returned records."},
 insert: {sql:"INSERT INTO knowledge\n(title, content, category, source, tags)\nVALUES\n('Cloud Computing', 'Delivery of computing services over the internet.',\n 'Technology', 'Class notes', 'cloud, computing');", explain:"INSERT INTO adds a new row to the knowledge table. Each value corresponds to a column listed in the INSERT statement."},
 update: {sql:"UPDATE knowledge\nSET category = 'Technology'\nWHERE id = 3;", explain:"UPDATE changes existing records. The WHERE clause is essential: without it, every row in the table could be modified."},
 delete: {sql:"DELETE FROM knowledge\nWHERE id = 3;", explain:"DELETE removes matching rows. Always verify the WHERE condition first, and consider a transaction or backup for important data."}
};
function toast(message){const el=$("#toast");el.textContent=message;el.classList.add("show");setTimeout(()=>el.classList.remove("show"),2600)}
function setSql(key){document.querySelectorAll(".sql-tab").forEach(b=>b.classList.toggle("active",b.dataset.query===key));$("#sqlCode").textContent=examples[key].sql;$("#sqlExplain").textContent=examples[key].explain}
document.querySelectorAll(".sql-tab").forEach(b=>b.addEventListener("click",()=>setSql(b.dataset.query)));
$("#copySql").addEventListener("click",async()=>{try{await navigator.clipboard.writeText($("#sqlCode").textContent);toast("SQL query copied.")}catch{toast("Copy is not available in this browser.")}});
$("#menuBtn").addEventListener("click",()=>$("#nav").classList.toggle("open"));
document.querySelectorAll("#nav a").forEach(a=>a.addEventListener("click",()=>$("#nav").classList.remove("open")));
let records=[];
async function loadStats(){try{const r=await fetch("/api/stats");const d=await r.json();$("#statTotal").textContent=d.total??"—";$("#statCategories").textContent=d.categories??"—";$("#statSources").textContent=d.sources??"—"}catch{}}
async function loadKnowledge(){
  const q=$("#searchInput").value.trim(), category=$("#categoryFilter").value;
  const params=new URLSearchParams();if(q)params.set("q",q);if(category)params.set("category",category);
  $("#knowledgeGrid").innerHTML='<div class="loading-card">Searching knowledge records...</div>';
  try{
    const r=await fetch("/api/knowledge?"+params.toString());const data=await r.json();
    if(!r.ok)throw new Error(data.error||"Database unavailable");
    records=data;renderRecords(data);
  }catch(e){$("#knowledgeGrid").innerHTML='<div class="loading-card">Unable to connect to MySQL. Start the database and run schema.sql, then refresh this page.</div>';$("#resultCount").textContent="Database connection required";}
}
function renderRecords(items){
  $("#resultCount").textContent=`${items.length} record${items.length===1?"":"s"} found`;
  $("#emptyState").classList.toggle("hidden",items.length>0);
  $("#knowledgeGrid").innerHTML=items.map(r=>`<article class="knowledge-card"><span class="category">${esc(r.category)}</span><h3>${esc(r.title)}</h3><p>${esc(r.content)}</p><footer><span>${esc(r.source||"UKD")} · #${r.id}</span><button class="delete-record" data-id="${r.id}" title="Delete record" aria-label="Delete record">Delete ×</button></footer></article>`).join("");
  document.querySelectorAll(".delete-record").forEach(b=>b.addEventListener("click",()=>removeRecord(b.dataset.id)));
}
let searchTimer;$("#searchInput").addEventListener("input",()=>{clearTimeout(searchTimer);searchTimer=setTimeout(loadKnowledge,250)});$("#categoryFilter").addEventListener("change",loadKnowledge);
const modal=$("#modal");$("#addOpen").addEventListener("click",()=>modal.classList.remove("hidden"));$("#modalClose").addEventListener("click",()=>modal.classList.add("hidden"));modal.addEventListener("click",e=>{if(e.target===modal)modal.classList.add("hidden")});
$("#knowledgeForm").addEventListener("submit",async e=>{
 e.preventDefault();$("#formError").textContent="";
 const data=Object.fromEntries(new FormData(e.currentTarget).entries());
 try{const r=await fetch("/api/knowledge",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data)});const out=await r.json();if(!r.ok)throw new Error(out.error||"Could not save record");e.currentTarget.reset();modal.classList.add("hidden");toast("Knowledge record added successfully.");await loadKnowledge();await loadStats()}catch(err){$("#formError").textContent=err.message}
});
async function removeRecord(id){if(!confirm("Delete this knowledge record?"))return;try{const r=await fetch(`/api/knowledge/${id}`,{method:"DELETE"});const d=await r.json();if(!r.ok)throw new Error(d.error);toast("Record deleted.");await loadKnowledge();await loadStats()}catch(e){toast(e.message)}}
setSql("select");loadStats();loadKnowledge();
