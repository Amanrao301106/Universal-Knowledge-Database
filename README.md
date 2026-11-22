# Universal Knowledge Database (UKD) — Deployment-ready React edition

Full-stack DBMS project:
- React + Vite frontend
- Python Flask REST API
- MySQL database
- Vercel (frontend) + Render (backend) + Aiven MySQL (database) deployment path

## 1. Local setup

### MySQL
1. Start MySQL Server.
2. Open MySQL Workbench or the MySQL command line.
3. Execute the root `schema.sql` file.

### Flask backend
From the project root:

```bash
python -m venv venv
```

Windows:
```bash
venv\Scripts\activate
```

macOS/Linux:
```bash
source venv/bin/activate
```

Install and configure:
```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set your local MySQL credentials. For local use:
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_local_mysql_password
DB_NAME=universal_knowledge_db
FRONTEND_ORIGINS=http://localhost:5173
```

Start Flask:
```bash
python app.py
```

### React frontend
In a second terminal:
```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL (normally `http://localhost:5173`). Vite proxies `/api` calls to Flask locally.

## 2. Push the project to GitHub

1. Create a new GitHub repository, e.g. `universal-knowledge-database`.
2. Extract this project ZIP.
3. Open the extracted project folder in VS Code.
4. Make sure `.env` is NOT committed. It contains secrets.
5. In the terminal:

```bash
git init
git add .
git commit -m "Prepare UKD full-stack project for deployment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/universal-knowledge-database.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

## 3. Create the cloud MySQL database (Aiven)

1. Create/sign in to an Aiven account.
2. Create an Aiven for MySQL service and wait until it is running.
3. Open the service's connection information and note its host, port, username and password.
4. Create/use the database named `universal_knowledge_db` (or keep the database name supplied by Aiven and use that exact name in the environment variable).
5. Download the CA certificate if you want certificate verification.
6. Connect to the cloud database with MySQL Workbench using the host, port, username and password; enable SSL and select the downloaded CA certificate where required.
7. Run the root `schema.sql` against the cloud database.

Aiven plans and availability can vary. Check the current plan and pricing before creating a service.

## 4. Deploy Flask backend on Render

1. Sign in to Render and connect your GitHub account.
2. Select **New → Web Service** and choose this repository.
3. Configure:
   - Runtime: `Python`
   - Root Directory: leave blank
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
4. Add these environment variables in Render (use your actual Aiven values):
   - `DB_HOST` = Aiven host
   - `DB_PORT` = Aiven port (often not 3306; use the value shown by Aiven)
   - `DB_USER` = Aiven username
   - `DB_PASSWORD` = Aiven password
   - `DB_NAME` = `universal_knowledge_db` (or your actual database name)
   - `FRONTEND_ORIGINS` = temporary `http://localhost:5173`; update after Vercel deployment
   - Optional `DB_SSL_CA` = path to CA certificate only if you have included the certificate in the backend deployment and want certificate verification
5. Deploy the service.
6. Copy its public URL, e.g. `https://your-ukd-api.onrender.com`.
7. Test `https://your-ukd-api.onrender.com/api/health`. It should return `{"api":"running","database":"connected"}`.

Render's free web services may spin down after inactivity; the first request after idle time can take longer.

## 5. Deploy React frontend on Vercel

1. Sign in to Vercel and import the same GitHub repository.
2. Set **Root Directory** to `frontend`.
3. Framework preset: `Vite`.
4. Build Command: `npm run build`.
5. Output Directory: `dist`.
6. Add environment variable:
   - `VITE_API_URL` = your Render backend URL, e.g. `https://your-ukd-api.onrender.com`
7. Deploy.
8. Copy the Vercel URL, e.g. `https://your-ukd.vercel.app`.

Vite exposes `VITE_` variables in the browser bundle. Never put database passwords or private credentials in a `VITE_` variable.

## 6. Connect frontend CORS to the deployed backend

Go back to Render → your backend service → Environment.

Set:
```env
FRONTEND_ORIGINS=https://your-ukd.vercel.app
```

Use your actual Vercel domain. Save and redeploy/restart the Render service.

## 7. Final verification

Open the Vercel website and test:
- Home page and all navigation sections
- Knowledge records load from MySQL
- Search and category filtering work
- Add a record, refresh the page, and confirm it persists
- Delete a test record
- Render API `/api/health` reports database connected

## Security notes
- Never commit `.env` or share database passwords.
- Never place DB credentials in React/Vite environment variables.
- The API currently has no user login/role-based access. Anyone who can access the public API can add or delete records. For a public production website, add authentication and authorization before sharing write access widely.
- Restrict `FRONTEND_ORIGINS` to your actual frontend domain.
- Keep database backups and use TLS for database connections.

## API endpoints
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/stats` | Dashboard counts |
| GET | `/api/knowledge?q=&category=` | Search/filter |
| POST | `/api/knowledge` | Add a record |
| DELETE | `/api/knowledge/<id>` | Delete a record |
| GET | `/api/health` | Backend/database health |

## Folder layout
```text
universal_knowledge_database/
├── app.py
├── schema.sql
├── requirements.txt
├── .env.example
├── README.md
└── frontend/
    ├── package.json
    ├── vite.config.js
    ├── vercel.json
    ├── index.html
    └── src/
        ├── main.jsx
        ├── App.jsx
        └── styles.css
```
