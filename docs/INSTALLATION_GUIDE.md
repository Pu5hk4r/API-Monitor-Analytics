# 🚀 Installation Guide - Step by Step

This guide will walk you through setting up the API Monitor System from scratch.

## 📋 Prerequisites Checklist

Before starting, ensure you have:

- [ ] Computer with Linux, macOS, or Windows
- [ ] Google account for Firebase and Google Cloud
- [ ] Credit card for Google Cloud (free tier available)
- [ ] Terminal/Command line access
- [ ] Internet connection

## Part 1: Install Required Software

### 1. Install Python 3.11+

**macOS:**
```bash
brew install python@3.11
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

**Windows:**
Download from https://www.python.org/downloads/

Verify installation:
```bash
python3 --version  # Should show 3.11 or higher
```

### 2. Install Node.js 18+

**macOS:**
```bash
brew install node
```

**Ubuntu/Debian:**
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

**Windows:**
Download from https://nodejs.org/

Verify installation:
```bash
node --version  # Should show v18 or higher
npm --version
```

### 3. Install Docker (Optional but Recommended)

**macOS:**
Download Docker Desktop from https://www.docker.com/products/docker-desktop

**Ubuntu:**
```bash
sudo apt update
sudo apt install docker.io docker-compose
sudo usermod -aG docker $USER
# Log out and back in
```

**Windows:**
Download Docker Desktop from https://www.docker.com/products/docker-desktop

Verify:
```bash
docker --version
docker-compose --version
```

### 4. Install Git

**macOS:**
```bash
brew install git
```

**Ubuntu/Debian:**
```bash
sudo apt install git
```

**Windows:**
Download from https://git-scm.com/download/win

Verify:
```bash
git --version
```

## Part 2: Set Up Google Cloud and Firebase

### Step 1: Create Google Cloud Project

1. Go to https://console.cloud.google.com/
2. Click "Select a project" → "New Project"
3. Name: "api-monitor-system"
4. Click "Create"
5. Wait for project creation (30 seconds)

### Step 2: Enable Required APIs

1. In Google Cloud Console, go to "APIs & Services" → "Library"
2. Search and enable these APIs:
   - Cloud Logging API
   - Compute Engine API (if deploying to VM)

### Step 3: Get Gemini API Key

1. Go to https://makersuite.google.com/app/apikey
2. Click "Create API key"
3. Select your project
4. Copy the API key
5. Save it securely (you'll need it later)

### Step 4: Create Firebase Project

1. Go to https://console.firebase.google.com/
2. Click "Add project"
3. Select your Google Cloud project "api-monitor-system"
4. Accept terms and click "Continue"
5. Disable Google Analytics (optional)
6. Click "Create project"
7. Wait for setup (1-2 minutes)

### Step 5: Enable Firebase Authentication

1. In Firebase Console, click "Authentication"
2. Click "Get started"
3. Click "Email/Password"
4. Enable "Email/Password"
5. Click "Save"

### Step 6: Create Firestore Database

1. Click "Firestore Database" in left menu
2. Click "Create database"
3. Select "Start in production mode"
4. Choose location (select closest to your users)
5. Click "Enable"
6. Wait for database creation

### Step 7: Set Firestore Security Rules

1. Click "Rules" tab
2. Replace with:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /monitors/{monitorId} {
      allow read, write: if request.auth != null && 
                          resource.data.user_id == request.auth.uid;
      allow create: if request.auth != null;
    }
    
    match /alerts/{alertId} {
      allow read: if request.auth != null && 
                   resource.data.user_id == request.auth.uid;
    }
  }
}
```

3. Click "Publish"

### Step 8: Get Firebase Web Config

1. Go to Project Settings (gear icon)
2. Scroll to "Your apps"
3. Click web icon (</>)
4. Register app: name it "API Monitor Web"
5. Copy the `firebaseConfig` object
6. Save it (you'll need it for frontend)

Example:
```javascript
{
  apiKey: "AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  authDomain: "api-monitor-system.firebaseapp.com",
  projectId: "api-monitor-system",
  storageBucket: "api-monitor-system.appspot.com",
  messagingSenderId: "123456789012",
  appId: "1:123456789012:web:abcdef1234567890"
}
```

### Step 9: Download Firebase Admin SDK Key

1. Go to Project Settings → Service Accounts
2. Click "Generate new private key"
3. Click "Generate key"
4. Save the JSON file as `firebase-credentials.json`
5. Keep it secure (don't share it!)

## Part 3: Download and Set Up the Project

### Step 1: Download the Project

If you received a ZIP file:
```bash
# Extract the ZIP
unzip api-monitor-system.zip
cd api-monitor-system
```

Or clone from Git:
```bash
git clone <repository-url>
cd api-monitor-system
```

### Step 2: Run Setup Script

```bash
chmod +x setup.sh
./setup.sh
```

This will:
- Create Python virtual environment
- Install Python dependencies
- Install Node.js dependencies
- Create .env template files

### Step 3: Configure Backend

1. Open `backend/.env` in a text editor:
```bash
nano backend/.env
# or
code backend/.env
```

2. Update these values:
```env
FIREBASE_PROJECT_ID=api-monitor-system  # Your project ID
GCP_PROJECT_ID=api-monitor-system       # Same as above
GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXX     # From Step 2.3
ALLOWED_ORIGINS=["http://localhost:3000"]
```

3. Save and close

### Step 4: Add Firebase Credentials

```bash
# Create secrets directory
mkdir -p backend/secrets

# Copy your firebase-credentials.json
cp ~/Downloads/firebase-credentials.json backend/secrets/
```

### Step 5: Configure Frontend

1. Open `frontend/.env`:
```bash
nano frontend/.env
# or
code frontend/.env
```

2. Update with your Firebase config from Step 2.8:
```env
VITE_API_URL=http://localhost:8000
VITE_FIREBASE_API_KEY=AIzaSyXXXXXXXXXXXXX
VITE_FIREBASE_AUTH_DOMAIN=api-monitor-system.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=api-monitor-system
VITE_FIREBASE_STORAGE_BUCKET=api-monitor-system.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=123456789012
VITE_FIREBASE_APP_ID=1:123456789012:web:abcdef1234567890
```

3. Save and close

## Part 4: Run the Application

### Option A: Local Development (Recommended for First Run)

#### Terminal 1 - Backend:
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python main.py
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

#### Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```

You should see:
```
  VITE v5.0.11  ready in 500 ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

### Option B: Docker Compose

```bash
cd infrastructure
docker-compose up -d
```

Check logs:
```bash
docker-compose logs -f
```

## Part 5: Test the Application

### 1. Open Your Browser

Navigate to: http://localhost:3000

### 2. Create an Account

1. Click "Sign Up"
2. Enter your email and password (min 6 characters)
3. Click "Sign Up"
4. You'll be redirected to the dashboard

### 3. Create Your First Monitor

1. Click "Monitors" in the sidebar
2. Click "Add Monitor"
3. Fill in:
   - Name: "Test Monitor"
   - URL: "https://httpbin.org/status/200"
   - Method: GET
   - Expected Status: 200
4. Click "Create"

### 4. View Monitor Status

1. Wait 5 minutes for first check (or restart backend to trigger immediately)
2. Refresh the page
3. You should see status update to "Online"
4. Click the monitor to see details and charts

### 5. Test Backend API

Open http://localhost:8000/docs in your browser to see API documentation.

## Part 6: Troubleshooting

### Backend Won't Start

**Error: "Module not found"**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

**Error: "Firebase credentials not found"**
```bash
# Check file exists
ls -la backend/secrets/firebase-credentials.json

# If missing, copy it again
cp ~/Downloads/firebase-credentials.json backend/secrets/
```

**Error: "Port 8000 already in use"**
```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn main:app --port 8001
```

### Frontend Won't Start

**Error: "Cannot find module"**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Error: "Port 3000 already in use"**
```bash
# Kill process
lsof -ti:3000 | xargs kill -9
```

### Firebase Authentication Error

1. Check `.env` files have correct Firebase config
2. Verify Firebase Authentication is enabled
3. Check browser console for errors (F12)
4. Try clearing browser cache

### Can't Create Monitor

1. Check backend is running (http://localhost:8000/health)
2. Check browser console for errors
3. Verify you're logged in
4. Check Firestore rules are set correctly

### Database Error

```bash
# Recreate database
cd backend
rm -f database/metrics.db
python -c "from app.database.sqlite_db import init_database; init_database()"
```

## Part 7: Next Steps

### Production Deployment

See `docs/DEPLOYMENT_GUIDE.md` for:
- Deploying to Google Cloud
- Setting up SSL certificates
- Configuring domain name
- Production optimization

### Customization

- Add more monitors
- Adjust check intervals
- Customize alert thresholds
- Add custom headers
- Configure different HTTP methods

### Monitoring

- View real-time status
- Check response time charts
- Review alert history
- Export metrics

## 🎉 Success!

You now have a fully functional API monitoring system!

### Quick Reference

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Getting Help

- Check `docs/` folder for more guides
- Review `QUICK_REFERENCE.md` for common commands
- Check logs for errors
- Ensure all prerequisites are met

### Common Tasks

**Stop the application:**
```bash
# Local: Press Ctrl+C in both terminals
# Docker: docker-compose down
```

**Update the code:**
```bash
git pull
cd backend && source venv/bin/activate && pip install -r requirements.txt
cd ../frontend && npm install
```

**View logs:**
```bash
# Backend: Check terminal output
# Docker: docker-compose logs -f backend
```

---

**Congratulations!** You've successfully installed the API Monitor System! 🎊
