import os
import tempfile
from contextlib import contextmanager

import mysql.connector
import streamlit as st
from mysql.connector import Error

st.set_page_config(
    page_title="UKD — Universal Knowledge Database",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------- Theme / CSS -----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
:root { --ukd-cyan:#58e0e8; --ukd-blue:#7791ff; }
.stApp { background: radial-gradient(circle at 8% 5%, #13243a 0, transparent 28%), #080b12; color:#eef4ff; }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
h1,h2,h3 { font-family:'Space Grotesk',sans-serif !important; letter-spacing:-.7px; }
.block-container { max-width:1200px; padding-top:2rem; padding-bottom:3rem; }
.hero {
  padding:2.2rem 2.3rem; border:1px solid #294157; border-radius:18px;
  background: radial-gradient(circle at 88% 10%, #1b4051 0, transparent 38%), linear-gradient(130deg,#142333,#0e1520);
  margin-bottom:1.3rem;
}
.eyebrow { color:#58e0e8; letter-spacing:2px; font-size:.72rem; font-weight:700; }
.hero-title { font-family:'Space Grotesk',sans-serif; font-size:clamp(2.8rem,6vw,5rem); line-height:1.0; font-weight:700; letter-spacing:-3px; margin:.8rem 0; }
.gradient { background:linear-gradient(100deg,#62e8e4 5%,#7b9cff 55%,#b79aff); -webkit-background-clip:text; color:transparent; }
.hero-copy { max-width:650px; color:#a0aec1; font-size:1.05rem; line-height:1.8; }
.panel {
  background:linear-gradient(145deg,#121d2b,#0e1520); border:1px solid #26374b;
  border-radius:13px; padding:1.1rem 1.2rem; min-height:130px;
}
.panel-label { color:#8fa1b8; font-size:.72rem; letter-spacing:1.4px; text-transform:uppercase; }
.panel-value { color:#eafaff; font-family:'Space Grotesk',sans-serif; font-size:2rem; font-weight:700; margin-top:.35rem; }
.panel-text { color:#91a0b4; font-size:.88rem; line-height:1.6; margin-top:.4rem; }
.section-kicker { color:#58e0e8; font-size:.72rem; letter-spacing:2px; font-weight:700; margin-bottom:.35rem; }
.section-intro { color:#91a0b4; max-width:760px; line-height:1.75; }
div[data-testid="stMetric"] { background:#111a27; border:1px solid #26374b; padding:15px; border-radius:12px; }
div[data-testid="stMetricLabel"] { color:#8fa1b8; }
div[data-testid="stMetricValue"] { color:#eafaff; }
.stTabs [data-baseweb="tab-list"] { gap:8px; border-bottom:1px solid #29374a; }
.stTabs [data-baseweb="tab"] { background:#111a27; border:1px solid #29374a; border-radius:8px 8px 0 0; padding:10px 18px; color:#b7c7d9; }
.stTabs [aria-selected="true"] { color:#58e0e8 !important; border-color:#397080 !important; }
div.stButton > button, div.stFormSubmitButton > button {
  border-radius:8px; border:1px solid #45627a; background:linear-gradient(110deg,#55dce2,#7791ff);
  color:#07101a; font-weight:700; min-height:2.6rem;
}
div.stButton > button:hover, div.stFormSubmitButton > button:hover { border-color:#58e0e8; color:#07101a; }
div[data-testid="stExpander"] { background:#101824; border:1px solid #29374a; border-radius:10px; }
.arch-step { background:#111a27; border:1px solid #2a4157; border-radius:10px; padding:1rem; text-align:center; }
.arch-step strong { color:#dffcff; }
.arch-step small { color:#91a0b4; }
.schema-head { background:#172335; border:1px solid #29374b; border-radius:8px 8px 0 0; padding:.75rem 1rem; color:#58e0e8; font-weight:700; }
.schema-row { display:flex; justify-content:space-between; gap:1rem; padding:.65rem 1rem; background:#111a27; border:1px solid #202d3e; border-top:0; color:#d1ddeb; font-size:.86rem; }
.schema-row span:last-child { color:#8294aa; font-size:.78rem; text-align:right; }
div[data-testid="stAlert"] { border-radius:9px; }
footer { visibility:hidden; }
</style>
""", unsafe_allow_html=True)


# ----------------------------- Database helpers -----------------------------
def get_mysql_config():
    """Read credentials from Streamlit secrets first, then environment variables."""
    if "mysql" in st.secrets:
        cfg = dict(st.secrets["mysql"])
    else:
        cfg = {
            "host": os.getenv("DB_HOST", ""),
            "port": os.getenv("DB_PORT", "3306"),
            "user": os.getenv("DB_USER", ""),
            "password": os.getenv("DB_PASSWORD", ""),
            "database": os.getenv("DB_NAME", "universal_knowledge_db"),
        }
        ca = os.getenv("DB_SSL_CA", "")
        if ca:
            cfg["ssl_ca"] = ca

    required = ["host", "user", "password", "database"]
    if not all(str(cfg.get(k, "")).strip() for k in required):
        return None

    cfg["port"] = int(cfg.get("port", 3306))
    ca_text = cfg.pop("ca_cert", None)
    if ca_text:
        ca_path = os.path.join(tempfile.gettempdir(), "ukd_mysql_ca.pem")
        with open(ca_path, "w", encoding="utf-8") as f:
            f.write(str(ca_text))
        cfg["ssl_ca"] = ca_path
        cfg["ssl_verify_cert"] = True
        cfg["ssl_verify_identity"] = True
    return cfg


@contextmanager
def db_cursor(dictionary=True):
    cfg = get_mysql_config()
    if not cfg:
        raise RuntimeError("MySQL credentials are not configured yet. Add them in Streamlit Secrets.")
    conn = mysql.connector.connect(connection_timeout=10, **cfg)
    cur = conn.cursor(dictionary=dictionary)
    try:
        yield conn, cur
    finally:
        cur.close()
        conn.close()


def fetch_stats():
    with db_cursor() as (_, cur):
        cur.execute("SELECT COUNT(*) AS total FROM knowledge")
        total = cur.fetchone()["total"]
        cur.execute("SELECT COUNT(DISTINCT category) AS categories FROM knowledge")
        cats = cur.fetchone()["categories"]
        cur.execute("SELECT COUNT(DISTINCT source) AS sources FROM knowledge")
        sources = cur.fetchone()["sources"]
    return total, cats, sources


def fetch_knowledge(search="", category=""):
    sql = """SELECT id, title, content, category, source, tags, created_at
             FROM knowledge
             WHERE (%s = '' OR category = %s)
               AND (%s = '' OR title LIKE %s OR content LIKE %s OR tags LIKE %s)
             ORDER BY created_at DESC"""
    like = f"%{search}%"
    with db_cursor() as (_, cur):
        cur.execute(sql, (category, category, search, like, like, like))
        return cur.fetchall()


def insert_knowledge(data):
    with db_cursor(dictionary=False) as (conn, cur):
        cur.execute(
            """INSERT INTO knowledge (title, content, category, source, tags)
               VALUES (%s, %s, %s, %s, %s)""",
            (data["title"].strip(), data["content"].strip(), data["category"],
             data.get("source", "").strip() or "User contribution",
             data.get("tags", "").strip())
        )
        conn.commit()


def update_knowledge(record_id, title, content, category, source, tags):
    with db_cursor(dictionary=False) as (conn, cur):
        cur.execute(
            """UPDATE knowledge
               SET title=%s, content=%s, category=%s, source=%s, tags=%s
               WHERE id=%s""",
            (title.strip(), content.strip(), category, source.strip(), tags.strip(), record_id)
        )
        conn.commit()
        return cur.rowcount


def delete_knowledge(record_id):
    with db_cursor(dictionary=False) as (conn, cur):
        cur.execute("DELETE FROM knowledge WHERE id=%s", (record_id,))
        conn.commit()
        return cur.rowcount


def db_status():
    try:
        with db_cursor() as (_, cur):
            cur.execute("SELECT 1 AS ok")
            cur.fetchone()
        return True, "MySQL connected"
    except Exception as exc:
        return False, str(exc)


# ----------------------------- UI helpers -----------------------------
def heading(kicker, title, description):
    st.markdown(f'<div class="section-kicker">{kicker}</div><h2>{title}</h2><p class="section-intro">{description}</p>', unsafe_allow_html=True)


def render_schema(title, fields):
    st.markdown(f'<div class="schema-head">{title}</div>', unsafe_allow_html=True)
    for name, dtype in fields:
        st.markdown(f'<div class="schema-row"><span>{name}</span><span>{dtype}</span></div>', unsafe_allow_html=True)


def render_sql_lab():
    examples = {
        "SELECT": (
            "SELECT id, title, category\nFROM knowledge\nWHERE category = 'Computer Science'\nORDER BY created_at DESC;",
            "SELECT retrieves records. WHERE filters rows, and ORDER BY sorts the result."
        ),
        "INSERT": (
            "INSERT INTO knowledge\n(title, content, category, source, tags)\nVALUES\n('Cloud Computing', 'Delivery of computing services over the internet.',\n 'Technology', 'Class notes', 'cloud, computing');",
            "INSERT INTO adds a new row. The values must match the columns in the specified order."
        ),
        "UPDATE": (
            "UPDATE knowledge\nSET category = 'Technology'\nWHERE id = 3;",
            "UPDATE modifies existing records. Always use a WHERE clause to target the intended row."
        ),
        "DELETE": (
            "DELETE FROM knowledge\nWHERE id = 3;",
            "DELETE removes matching records. Verify the WHERE clause before executing."
        )
    }
    op = st.radio("Choose SQL operation", list(examples), horizontal=True, key="sql_operation")
    query, explain = examples[op]
    st.code(query, language="sql")
    st.info(explain)
    st.caption("Educational examples only. This panel displays SQL; it does not execute arbitrary SQL entered by visitors.")


# ----------------------------- Sidebar -----------------------------
with st.sidebar:
    st.markdown("## 🌐 UKD.")
    st.caption("UNIVERSAL KNOWLEDGE DATABASE")
    page = st.radio(
        "NAVIGATION",
        ["Overview", "Knowledge Explorer", "Database Design", "SQL Lab", "Applications & Conclusion"],
        label_visibility="visible"
    )
    st.divider()
    connected, status_message = db_status()
    if connected:
        st.success("● " + status_message)
    else:
        st.warning("● MySQL not configured")
        with st.expander("Connection details"):
            st.caption("Configure the [mysql] section in Streamlit Secrets after your cloud database is ready.")
            st.code('[mysql]\nhost = "YOUR_HOST"\nport = 3306\nuser = "YOUR_USER"\npassword = "YOUR_PASSWORD"\ndatabase = "universal_knowledge_db"', language="toml")
    st.caption("DBMS PROJECT · REACT-FREE STREAMLIT EDITION")


# ----------------------------- Header -----------------------------
st.markdown("""
<div class="hero">
  <div class="eyebrow">DATABASE MANAGEMENT SYSTEM · PROJECT</div>
  <div class="hero-title">Knowledge has<br>no <span class="gradient">boundaries.</span></div>
  <div class="hero-copy">One intelligent place to collect, connect, organize and discover information across every domain.</div>
</div>
""", unsafe_allow_html=True)

if page == "Overview":
    heading("01 — THE CONCEPT", "What is UKD?", "A centralized knowledge platform designed to make information easier to store, manage, relate and retrieve.")
    a, b, c = st.columns(3)
    with a:
        st.markdown('<div class="panel"><div class="panel-label">THE BIG IDEA</div><div class="panel-value">Unified</div><div class="panel-text">Bring scattered information into one organized knowledge space.</div></div>', unsafe_allow_html=True)
    with b:
        st.markdown('<div class="panel"><div class="panel-label">DISCOVERY</div><div class="panel-value">Searchable</div><div class="panel-text">Find relevant records using keywords and category filters.</div></div>', unsafe_allow_html=True)
    with c:
        st.markdown('<div class="panel"><div class="panel-label">DATA QUALITY</div><div class="panel-value">Structured</div><div class="panel-text">Use relational tables, keys, indexes and constraints.</div></div>', unsafe_allow_html=True)

    st.markdown("### System architecture")
    cols = st.columns(4)
    steps = [
        ("01 · INPUT", "Documents", "Web sources · User entries"),
        ("02 · APP", "Python", "Streamlit · Validation"),
        ("03 · STORAGE", "MySQL", "Tables · Relationships"),
        ("04 · OUTPUT", "Insights", "Search · Records · Reports"),
    ]
    for col, (label, title, desc) in zip(cols, steps):
        with col:
            st.markdown(f'<div class="arch-step"><small>{label}</small><br><strong>{title}</strong><br><small>{desc}</small></div>', unsafe_allow_html=True)
    st.markdown("### Live database statistics")
    try:
        total, cats, sources = fetch_stats()
        x, y, z = st.columns(3)
        x.metric("Knowledge records", total)
        y.metric("Categories", cats)
        z.metric("Information sources", sources)
    except Exception:
        x, y, z = st.columns(3)
        x.metric("Knowledge records", "—")
        y.metric("Categories", "—")
        z.metric("Information sources", "—")
        st.info("Connect MySQL to display live statistics and enable the Knowledge Explorer.")

elif page == "Knowledge Explorer":
    heading("02 — LIVE DATABASE", "Knowledge Explorer", "Search the MySQL database, filter by category, and manage knowledge records.")
    c1, c2 = st.columns([2, 1])
    with c1:
        search = st.text_input("Search knowledge", placeholder="Search titles, descriptions or tags...")
    with c2:
        selected_category = st.selectbox("Filter category", ["All categories", "Computer Science", "Artificial Intelligence", "Science", "Mathematics", "Healthcare", "History", "Technology"])
    category_value = "" if selected_category == "All categories" else selected_category

    with st.expander("＋ Add a knowledge record", expanded=False):
        with st.form("add_knowledge_form", clear_on_submit=True):
            title = st.text_input("Title", max_chars=180)
            category = st.selectbox("Category", ["Computer Science", "Artificial Intelligence", "Science", "Mathematics", "Healthcare", "History", "Technology"])
            content = st.text_area("Knowledge / Description", height=120)
            source = st.text_input("Source", placeholder="Book, website, class notes...")
            tags = st.text_input("Tags", placeholder="database, SQL, learning")
            submitted = st.form_submit_button("Save knowledge record")
            if submitted:
                if not title.strip() or not content.strip():
                    st.error("Title and description are required.")
                else:
                    try:
                        insert_knowledge({"title": title, "content": content, "category": category, "source": source, "tags": tags})
                        st.success("Knowledge record saved.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Could not save record: {exc}")

    try:
        rows = fetch_knowledge(search, category_value)
        st.caption(f"{len(rows)} record(s) found")
        if not rows:
            st.info("No matching records. Try another search or add a new entry.")
        for row in rows:
            title_line = f"{row['title']}  ·  {row['category']}  ·  #{row['id']}"
            with st.expander(title_line):
                st.write(row["content"])
                st.caption(f"Source: {row.get('source') or 'Not specified'}  |  Tags: {row.get('tags') or '—'}")
                with st.form(f"edit_{row['id']}"):
                    st.markdown("**Edit record**")
                    new_title = st.text_input("Title", value=row["title"], key=f"title_{row['id']}")
                    new_category = st.selectbox("Category", ["Computer Science", "Artificial Intelligence", "Science", "Mathematics", "Healthcare", "History", "Technology"], index=(["Computer Science", "Artificial Intelligence", "Science", "Mathematics", "Healthcare", "History", "Technology"].index(row["category"]) if row["category"] in ["Computer Science", "Artificial Intelligence", "Science", "Mathematics", "Healthcare", "History", "Technology"] else 0), key=f"cat_{row['id']}")
                    new_content = st.text_area("Description", value=row["content"], key=f"content_{row['id']}")
                    new_source = st.text_input("Source", value=row.get("source") or "", key=f"source_{row['id']}")
                    new_tags = st.text_input("Tags", value=row.get("tags") or "", key=f"tags_{row['id']}")
                    save_edit = st.form_submit_button("Update record")
                    if save_edit:
                        try:
                            update_knowledge(row["id"], new_title, new_content, new_category, new_source, new_tags)
                            st.success("Record updated.")
                            st.rerun()
                        except Exception as exc:
                            st.error(f"Update failed: {exc}")
                if st.button("🗑️ Delete this record", key=f"delete_{row['id']}"):
                    try:
                        delete_knowledge(row["id"])
                        st.success("Record deleted.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Delete failed: {exc}")
    except Exception as exc:
        st.error(f"MySQL connection required: {exc}")
        st.markdown("Add your database credentials under **Streamlit app → Settings → Secrets** after provisioning a MySQL host.")

elif page == "Database Design":
    heading("03 — DATABASE DESIGN", "Structured at the core.", "A relational database stores knowledge records and organizes them with categories, attributes and constraints.")
    left, right = st.columns(2)
    with left:
        render_schema("TABLE 01 · knowledge", [
            ("🔑 id", "INT · PRIMARY KEY"),
            ("title", "VARCHAR(180)"),
            ("content", "TEXT"),
            ("category", "VARCHAR(80)"),
            ("source", "VARCHAR(180)"),
            ("tags", "VARCHAR(255)"),
            ("created_at", "TIMESTAMP"),
        ])
    with right:
        render_schema("TABLE 02 · categories", [
            ("🔑 id", "INT · PRIMARY KEY"),
            ("name", "VARCHAR(80) · UNIQUE"),
            ("description", "VARCHAR(255)"),
        ])
        st.markdown("### Relationship")
        st.info("One category can contain many knowledge records (one-to-many). The sample schema stores the category label in knowledge.category; a production-normalized version can use category_id as a foreign key.")
    st.markdown("### DBMS design principles")
    st.markdown("- **Primary key:** uniquely identifies each record.\n- **Unique constraint:** prevents duplicate category names.\n- **Indexes:** improve category lookup performance.\n- **Normalization:** reduces repeated data and supports consistency.\n- **Parameterized queries:** help protect database operations from SQL injection.")

elif page == "SQL Lab":
    heading("04 — DBMS OPERATIONS", "SQL playground.", "Explore the core SQL commands used to manage data in a relational database.")
    render_sql_lab()
    st.markdown("### CRUD mapping")
    st.table([
        {"Operation": "Create", "SQL": "INSERT", "UKD feature": "Add knowledge record"},
        {"Operation": "Read", "SQL": "SELECT", "UKD feature": "Search and filter records"},
        {"Operation": "Update", "SQL": "UPDATE", "UKD feature": "Edit a knowledge record"},
        {"Operation": "Delete", "SQL": "DELETE", "UKD feature": "Remove a knowledge record"},
    ])

else:
    heading("05 — REAL-WORLD VALUE", "One system. Many possibilities.", "A unified knowledge layer can support information discovery across different fields.")
    cols = st.columns(4)
    cases = [
        ("🎓", "Education", "Organize notes, concepts, learning resources and study material."),
        ("✚", "Healthcare", "Structure approved medical references and research information."),
        ("⌬", "Research", "Connect papers, findings, authors and related topics."),
        ("▤", "Business", "Centralize policies, process documentation and product knowledge."),
    ]
    for col, (icon, title, desc) in zip(cols, cases):
        with col:
            st.markdown(f'<div class="panel"><div class="panel-value">{icon}</div><b>{title}</b><div class="panel-text">{desc}</div></div>', unsafe_allow_html=True)
    st.markdown("### Conclusion")
    st.markdown("""
    Universal Knowledge Database demonstrates how DBMS concepts—structured storage,
    relationships, constraints, indexing and SQL operations—can create a useful foundation
    for unified knowledge management.
    """)
    st.success("One platform. Unlimited knowledge.")

st.divider()
st.caption("UNIVERSAL KNOWLEDGE DATABASE · DBMS PROJECT · Built with Streamlit, Python and MySQL")
