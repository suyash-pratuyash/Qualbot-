# QualBot

QualBot is a small lead-qualification demo. The FastAPI backend stores chat
history and BANT scores in SQLite; the React dashboard shows conversations and
lead tiers.

## Requirements

- Python 3.10 or newer
- Node.js and npm
- A Gemini API key stored in `backend\.env`

## Start the backend

Open PowerShell in the project folder. Create the virtual environment and
install backend packages if they are not already set up:

```powershell
cd D:\Projects-team\Qualbot\backend
py -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Create `backend\.env` and put your key there. The file is ignored by Git, so
your API key will not be committed:

```powershell
notepad .env
```

Add these lines to the file and replace the placeholder:

```dotenv
GEMINI_API_KEY=your_real_gemini_api_key
CALENDLY_URL=https://calendly.com/your-team/your-event
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

Save the file and start the API:

```powershell
python -m uvicorn main:app --reload
```

The backend loads `backend\.env` when its Gemini client module is imported.
Those file values take precedence over existing Windows environment variables.
Restart Uvicorn after changing `.env`.

Set `CORS_ALLOWED_ORIGINS` to a comma-separated list of the
exact frontend origins you use (for example, `http://localhost:5173`).

The API runs at `http://127.0.0.1:8000`. SQLite tables are initialized
automatically in `backend\qualbot.db`.

## Start the frontend

Open a second PowerShell terminal:

```powershell
cd D:\Projects-team\Qualbot\frontend
npm install
npm run dev
```

Open the Vite URL printed by npm (normally `http://localhost:5173`). The
frontend calls the API at `http://127.0.0.1:8000`; set `VITE_API_URL` before
`npm run dev` to use another backend URL.

## Try it

Use the **Chat** tab to start a conversation. The current chat session is saved
in the browser so reloading the page keeps its transcript. Use **New chat** for
a separate lead. The **Lead dashboard** tab lists saved leads; select a row to
see its transcript.

The chat API can also be called directly:

```powershell
$body = @{ session_id = "demo-1"; message = "I'm the founder and need a CRM this month." } | ConvertTo-Json
Invoke-RestMethod -Uri http://127.0.0.1:8000/chat -Method Post -ContentType "application/json" -Body $body
Invoke-RestMethod -Uri http://127.0.0.1:8000/leads
Invoke-RestMethod -Uri http://127.0.0.1:8000/leads/demo-1
```

If Gemini is unavailable, the API stays running and returns a fallback reply.
Live BANT extraction and AI replies require a valid API key and supported model
access.
