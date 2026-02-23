# 🚀 Quick Reference Guide

## Files Created

### Backend (FastAPI + Python)
```
backend/
├── main.py                              # FastAPI application
├── requirements.txt                     # Python dependencies
├── Dockerfile                           # Container image
├── .env.example                         # Environment template
└── app/
    ├── core/
    │   ├── config.py                    # Settings & config
    │   └── firebase.py                  # Firebase integration
    ├── database/
    │   └── sqlite_db.py                 # SQLite database
    ├── models/
    │   └── schemas.py                   # Pydantic models
    ├── routers/
    │   ├── monitors.py                  # Monitor endpoints
    │   ├── metrics.py                   # Metrics endpoints
    │   ├── alerts.py                    # Alert endpoints
    │   └── auth.py                      # Auth endpoints
    ├── scheduler/
    │   └── monitor_scheduler.py         # Background jobs
    └── services/
        ├── monitor_checker.py           # Health checker
        ├── gemini_service.py            # AI analysis
        └── cache_service.py             # In-memory cache
```

### Frontend (React + Vite)
```
frontend/
├── package.json                         # Node dependencies
├── vite.config.js                       # Vite configuration
├── tailwind.config.js                   # Tailwind CSS
├── postcss.config.js                    # PostCSS config
├── index.html                           # HTML template
└── src/
    ├── main.jsx                         # Entry point
    ├── App.jsx                          # Main component
    ├── index.css                        # Global styles
    ├── config/                          # Configurations
    ├── services/
    │   └── api.js                       # API client
    ├── components/                      # React components
    ├── pages/                           # Page components
    ├── context/                         # React context
    └── utils/                           # Utilities
```

### Infrastructure
```
infrastructure/
├── docker-compose.yml                   # Container orchestration
└── nginx/
    ├── nginx.conf                       # Main Nginx config
    └── conf.d/
        └── api-monitor.conf             # Server config
```

### Documentation
```
docs/
├── DEPLOYMENT_GUIDE.md                  # Full deployment guide
└── PROJECT_SUMMARY.md                   # Project overview
```

### Root Files
```
.
├── README.md                            # Main documentation
├── .gitignore                           # Git ignore rules
└── setup.sh                             # Setup script
```

## 📝 Quick Setup

### 1. Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (optional)
- Firebase project
- Google Cloud project with Gemini API

### 2. Run Setup Script
```bash
chmod +x setup.sh
./setup.sh
```

### 3. Configure Credentials

**Backend (.env)**
```env
FIREBASE_PROJECT_ID=your-project-id
GEMINI_API_KEY=your-gemini-key
ALLOWED_ORIGINS=["http://localhost:3000"]
```

**Frontend (.env)**
```env
VITE_API_URL=http://localhost:8000
VITE_FIREBASE_API_KEY=your-api-key
VITE_FIREBASE_PROJECT_ID=your-project-id
# ... other Firebase config
```

**Firebase Credentials**
- Download `firebase-credentials.json`
- Place in `backend/secrets/`

### 4. Run Development Servers

**Option A: Local Development**
```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
python main.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

**Option B: Docker Compose**
```bash
cd infrastructure
docker-compose up -d
```

### 5. Access Application
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 🔧 Common Commands

### Backend
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python main.py

# Run with auto-reload
uvicorn main:app --reload

# Create database
python -c "from app.database.sqlite_db import init_database; init_database()"
```

### Frontend
```bash
# Install dependencies
npm install

# Run dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Docker
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild images
docker-compose build

# Shell into container
docker exec -it api-monitor-backend bash
```

## 📊 API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/api/monitors/` | List monitors |
| POST | `/api/monitors/` | Create monitor |
| GET | `/api/monitors/{id}` | Get monitor |
| PUT | `/api/monitors/{id}` | Update monitor |
| DELETE | `/api/monitors/{id}` | Delete monitor |
| GET | `/api/monitors/{id}/health-checks` | Health history |
| GET | `/api/metrics/{id}` | Get metrics |
| GET | `/api/alerts/{id}` | Get alerts |
| GET | `/api/auth/me` | Current user |

## 🗄️ Database Tables

### Firestore Collections
- `monitors` - Monitor configurations
- `alerts` - Alert records
- `users` - User profiles (optional)

### SQLite Tables
- `health_checks` - Time-series health data
- `daily_metrics` - Aggregated daily stats

## 🔐 Required API Keys

1. **Firebase Admin SDK**
   - Project Settings → Service Accounts
   - Generate private key
   - Save as `firebase-credentials.json`

2. **Gemini API Key**
   - Visit: https://makersuite.google.com/app/apikey
   - Create API key
   - Add to `.env`

3. **Firebase Web Config**
   - Project Settings → General
   - Your apps → Web app
   - Copy config to frontend `.env`

## 🚀 Deployment Steps

### Quick Deploy to Google Cloud

```bash
# 1. Create VM
gcloud compute instances create api-monitor \
  --machine-type=e2-medium \
  --zone=us-central1-a

# 2. SSH and setup
gcloud compute ssh api-monitor
git clone <repo-url>
cd api-monitor-system

# 3. Deploy with Docker
cd infrastructure
docker-compose up -d

# 4. Setup SSL
docker-compose run --rm certbot certonly \
  --webroot -d api.yourdomain.com
```

## 🔍 Monitoring the Monitor

### Check Backend Health
```bash
curl http://localhost:8000/health
```

### View Database
```bash
sqlite3 backend/database/metrics.db
.tables
SELECT * FROM health_checks LIMIT 5;
```

### Check Logs
```bash
# Docker logs
docker-compose logs -f backend

# Application logs
tail -f backend/logs/app.log
```

## 🆘 Troubleshooting

### Port already in use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

### Firebase auth error
- Verify `firebase-credentials.json` exists
- Check Firebase project ID in `.env`
- Ensure Firestore is enabled

### Module not found
```bash
# Backend
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend
rm -rf node_modules
npm install
```

## 📚 Key Dependencies

### Backend
- fastapi==0.109.0 - Web framework
- uvicorn==0.27.0 - ASGI server
- firebase-admin==6.4.0 - Firebase SDK
- google-generativeai==0.3.2 - Gemini AI
- apscheduler==3.10.4 - Task scheduler
- httpx==0.26.0 - HTTP client
- pydantic==2.5.3 - Data validation

### Frontend
- react==18.2.0 - UI library
- vite==5.0.11 - Build tool
- tailwindcss==3.4.1 - CSS framework
- axios==1.6.5 - HTTP client
- firebase==10.7.2 - Firebase SDK
- chart.js==4.4.1 - Charts
- react-router-dom==6.21.0 - Routing

## 💡 Tips

1. **Use .env files** - Never commit secrets
2. **Enable debug mode** - Set `DEBUG=True` for development
3. **Test locally first** - Verify before deploying
4. **Monitor logs** - Watch for errors during operation
5. **Backup database** - Regular SQLite backups
6. **Update dependencies** - Keep packages current
7. **Use HTTPS** - Always in production
8. **Set up alerts** - Monitor the monitoring system!

## 📞 Next Steps

1. Read full documentation in `docs/`
2. Configure Firebase and Google Cloud
3. Run setup script
4. Start development servers
5. Create your first monitor
6. Deploy to production
7. Set up monitoring alerts
8. Add custom features

---

**Need help?** Check the full guides in the `docs/` directory!
