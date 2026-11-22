# Universal Knowledge Database — Streamlit Edition

A DBMS project website built with Streamlit, Python and MySQL.

## Included
- Modern dark technology theme
- Project overview and system architecture
- Database schema and relationship explanation
- MySQL-backed knowledge search and category filtering
- Add, edit and delete knowledge records
- Live database statistics
- SQL examples for SELECT, INSERT, UPDATE and DELETE
- Streamlit Community Cloud deployment support

## Important: hosting costs
Streamlit Community Cloud offers free app hosting. The MySQL database is a separate service and may have its own pricing. Do not assume the database host is free; check its current plan before signing up.

## Run locally
1. Install Python 3.10 or newer.
2. Start a MySQL server and execute `schema.sql`.
3. Create a virtual environment and install dependencies:

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
pip install -r requirements.txt
```

4. Configure MySQL credentials in `.streamlit/secrets.toml`:

```toml
[mysql]
host = "YOUR_MYSQL_HOST"
port = 3306
user = "YOUR_MYSQL_USER"
password = "YOUR_MYSQL_PASSWORD"
database = "universal_knowledge_db"
```

5. Run:

```bash
streamlit run streamlit_app.py
```

## Deploy on Streamlit Community Cloud
1. Push this project to a GitHub repository.
2. Visit https://share.streamlit.io/ and sign in with GitHub.
3. Click **Create app**.
4. Select the repository and branch.
5. Set the main file path to `streamlit_app.py`.
6. In **Advanced settings → Secrets**, add the TOML database configuration shown above using your real cloud MySQL credentials.
7. Deploy.

Never commit `.streamlit/secrets.toml` or expose database passwords. Add `.streamlit/secrets.toml` to `.gitignore`.

## Cloud MySQL note
Streamlit Community Cloud runs the Python app; it does not provide a managed MySQL server. Use a separate MySQL provider that permits remote connections from your app. Configure TLS/SSL according to that provider's instructions. The app supports a `ca_cert` multiline secret containing a trusted CA certificate:

```toml
[mysql]
host = "YOUR_HOST"
port = 3306
user = "YOUR_USER"
password = "YOUR_PASSWORD"
database = "universal_knowledge_db"
ca_cert = """-----BEGIN CERTIFICATE-----
PASTE_CA_CERTIFICATE_HERE
-----END CERTIFICATE-----"""
```

If your provider requires a different SSL configuration, adjust the connection helper accordingly.

## Security
The demonstration app has no login system. Anyone with access to the public app can add, edit or delete records. Use a database account with only the permissions required by this project, and add authentication before using it for sensitive information.
