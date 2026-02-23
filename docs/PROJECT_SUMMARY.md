# 🚀 API Monitor System - Project Summary

## Overview
A production-ready API monitoring system with real-time health checks, intelligent alerts powered by Google Gemini AI, and comprehensive metrics tracking.

## Tech Stack

### Backend
- **Framework**: FastAPI 0.109.0
- **Language**: Python 3.11
- **Database**: SQLite (time-series) + Firestore (configs)
- **Authentication**: Firebase Admin SDK
- **AI**: Google Gemini Pro
- **Scheduler**: APScheduler
- **Server**: Uvicorn with async support

### Frontend
- **Framework**: React 18.2
- **Build Tool**: Vite 5.0
- **Styling**: Tailwind CSS 3.4
- **Charts**: Chart.js 4.4
- **HTTP Client**: Axios
- **Authentication**: Firebase SDK

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Reverse Proxy**: Nginx (with rate limiting)
- **SSL**: Let's Encrypt via Certbot
- **Cloud**: Google Cloud Platform
- **Hosting**: GCE VM or Cloud Run + Firebase Hosting

## Key Features

### 1. Monitor Management
- Create/Read/Update/Delete monitors
- Support for GET, POST, PUT, DELETE, PATCH methods
- Custom headers and request bodies
- Configurable intervals (1-60 minutes)
- Timeout settings (5-120 seconds)
- Expected status code validation

### 2. Health Monitoring
- Automated health checks every 5 minutes
- Response time tracking (milliseconds)
- Status code monitoring
- Error message capture
- Historical data (7 days retention)
- Real-time status updates

### 3. Metrics & Analytics
- Uptime percentage (24h rolling)
- Average response time
- Response time percentiles (P50, P95, P99)
- Error rate calculation
- Daily aggregated metrics
- Time-series charts

### 4. Intelligent Alerts
- Consecutive failure detection (threshold: 3)
- Alert cooldown (30 minutes)
- AI-powered error analysis via Gemini
- Root cause suggestions
- Recommended actions
- Prevention tips

### 5. Performance
- In-memory caching (5-min TTL)
- Concurrent health checks (10 workers)
- Efficient SQLite storage
- Request rate limiting (100/min)
- Background job scheduling

## File Structure

```
api-monitor-system/
├── backend/
│   ├── main.py                 # FastAPI application entry
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py       # Environment configuration
│   │   │   └── firebase.py     # Firebase integration
│   │   ├── database/
│   │   │   └── sqlite_db.py    # Time-series database
│   │   ├── models/
│   │   │   └── schemas.py      # Pydantic models
│   │   ├── routers/
│   │   │   ├── monitors.py     # Monitor endpoints
│   │   │   ├── metrics.py      # Metrics endpoints
│   │   │   ├── alerts.py       # Alert endpoints
│   │   │   └── auth.py         # Auth endpoints
│   │   ├── scheduler/
│   │   │   └── monitor_scheduler.py  # Background jobs
│   │   └── services/
│   │       ├── monitor_checker.py    # Health checker
│   │       ├── gemini_service.py     # AI analysis
│   │       └── cache_service.py      # Caching
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx             # Main React component
│   │   ├── services/api.js     # API client
│   │   ├── config/firebase.js  # Firebase config
│   │   ├── components/         # React components
│   │   ├── pages/              # Page components
│   │   ├── context/            # React context
│   │   └── utils/              # Utilities
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
│
├── infrastructure/
│   ├── docker-compose.yml      # Container orchestration
│   ├── nginx/
│   │   ├── nginx.conf          # Main config
│   │   └── conf.d/
│   │       └── api-monitor.conf  # Server config
│
└── docs/
    ├── DEPLOYMENT_GUIDE.md     # Full deployment guide
    └── README.md               # Project documentation
```

## Quick Start Commands

### Local Development

```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Configure this
python main.py

# Frontend
cd frontend
npm install
cp .env.example .env  # Configure this
npm run dev

# Docker (All services)
cd infrastructure
docker-compose up -d
```

### Production Deployment

```bash
# Google Compute Engine
gcloud compute instances create api-monitor-vm \
  --machine-type=e2-medium \
  --zone=us-central1-a

# SSH and deploy
gcloud compute ssh api-monitor-vm
git clone <repo-url>
cd api-monitor-system/infrastructure
docker-compose up -d

# SSL Certificate
docker-compose run --rm certbot certonly \
  --webroot -d api.yourdomain.com
```

## Database Schema

### Firestore Collections

#### monitors
```javascript
{
  user_id: string,
  name: string,
  url: string,
  method: string,
  headers: object,
  body: string,
  interval_minutes: number,
  timeout_seconds: number,
  expected_status_code: number,
  alert_on_failure: boolean,
  is_active: boolean,
  created_at: timestamp,
  updated_at: timestamp
}
```

#### alerts
```javascript
{
  monitor_id: string,
  user_id: string,
  monitor_name: string,
  alert_type: string,
  message: string,
  details: object,
  ai_analysis: string,
  is_resolved: boolean,
  created_at: timestamp
}
```

### SQLite Tables

#### health_checks
```sql
CREATE TABLE health_checks (
    id INTEGER PRIMARY KEY,
    monitor_id TEXT NOT NULL,
    timestamp DATETIME NOT NULL,
    status_code INTEGER,
    response_time_ms INTEGER,
    is_up BOOLEAN NOT NULL,
    error_message TEXT,
    INDEX (monitor_id, timestamp)
);
```

#### daily_metrics
```sql
CREATE TABLE daily_metrics (
    id INTEGER PRIMARY KEY,
    monitor_id TEXT NOT NULL,
    date DATE NOT NULL,
    total_checks INTEGER,
    successful_checks INTEGER,
    failed_checks INTEGER,
    avg_response_time_ms REAL,
    p50_response_time_ms INTEGER,
    p95_response_time_ms INTEGER,
    p99_response_time_ms INTEGER,
    uptime_percent REAL,
    error_rate REAL,
    UNIQUE(monitor_id, date)
);
```

## API Endpoints Reference

### Monitors
- `GET /api/monitors/` - List monitors
- `POST /api/monitors/` - Create monitor
- `GET /api/monitors/{id}` - Get monitor
- `PUT /api/monitors/{id}` - Update monitor
- `DELETE /api/monitors/{id}` - Delete monitor
- `GET /api/monitors/{id}/health-checks` - Health history
- `GET /api/monitors/dashboard/stats` - Dashboard stats

### Metrics
- `GET /api/metrics/{id}?hours=24` - Monitor metrics
- `GET /api/metrics/{id}/daily?days=7` - Daily metrics

### Alerts
- `GET /api/alerts/{monitor_id}` - Monitor alerts
- `GET /api/alerts/` - All user alerts

### Auth
- `GET /api/auth/me` - Current user
- `GET /api/auth/verify` - Verify token

## Configuration Checklist

### Google Cloud
- [ ] Create GCP project
- [ ] Enable required APIs (Compute, Logging, AI Platform)
- [ ] Get Gemini API key
- [ ] Create service account
- [ ] Download service account key

### Firebase
- [ ] Create Firebase project
- [ ] Enable Authentication (Email/Password)
- [ ] Create Firestore database
- [ ] Set security rules
- [ ] Get Firebase config
- [ ] Download Admin SDK key

### Backend
- [ ] Copy `.env.example` to `.env`
- [ ] Add Firebase credentials path
- [ ] Add Gemini API key
- [ ] Configure ALLOWED_ORIGINS
- [ ] Place firebase-credentials.json

### Frontend
- [ ] Copy `.env.example` to `.env`
- [ ] Add Firebase config values
- [ ] Set API URL
- [ ] Build for production

### Infrastructure
- [ ] Update nginx server_name
- [ ] Configure SSL certificates
- [ ] Set up firewall rules
- [ ] Configure rate limiting
- [ ] Set up monitoring

## Environment Variables Summary

### Required
```env
FIREBASE_PROJECT_ID=your-firebase-project-id
GEMINI_API_KEY=your-gemini-api-key
ALLOWED_ORIGINS=["https://yourdomain.com"]
```

### Optional (with defaults)
```env
DEBUG=False
MONITOR_CHECK_INTERVAL_MINUTES=5
MAX_WORKERS=10
REQUEST_TIMEOUT_SECONDS=30
DATA_RETENTION_DAYS=7
CACHE_TTL_SECONDS=300
MAX_CONSECUTIVE_FAILURES=3
ALERT_COOLDOWN_MINUTES=30
```

## Cost Estimation (Monthly)

### Free Tier
- Firestore: 50K reads, 20K writes, 1GB storage
- Gemini: 60 requests/min (free tier)
- GCE e2-micro: Free tier eligible (1 instance)

### Low Traffic (~100 monitors)
- GCE e2-medium: ~$24/month
- Firestore: ~$5/month
- Cloud Logging: Free (within limits)
- **Total: ~$30/month**

### Medium Traffic (~500 monitors)
- GCE e2-standard-2: ~$48/month
- Firestore: ~$15/month
- Cloud Logging: ~$5/month
- **Total: ~$70/month**

## Monitoring & Alerts Flow

```
1. APScheduler triggers every 5 minutes
   ↓
2. Fetch active monitors from Firestore
   ↓
3. Concurrent health checks (10 workers)
   ↓
4. Record results to SQLite
   ↓
5. Update cache with current status
   ↓
6. Check alert conditions
   ↓
7. If failure threshold met:
   - Generate Gemini AI analysis
   - Create alert in Firestore
   - Reset on cooldown completion
```

## Security Layers

1. **Network**: HTTPS only, rate limiting
2. **Authentication**: Firebase ID tokens
3. **Authorization**: User-resource ownership checks
4. **Input Validation**: Pydantic schemas
5. **Database**: Parameterized queries
6. **Headers**: XSS, CSP, CORS protection
7. **Secrets**: Environment variables, volume mounts

## Scaling Strategy

### Vertical (Single Instance)
- Start with e2-medium (2 vCPU, 4GB RAM)
- Scale to e2-standard-2 (2 vCPU, 8GB RAM)
- Max: e2-standard-4 (4 vCPU, 16GB RAM)

### Horizontal (Multi-Instance)
1. Move SQLite → Cloud SQL (PostgreSQL)
2. Add Redis for distributed cache
3. Use Cloud Load Balancer
4. Deploy multiple backend instances
5. Use Cloud Run for auto-scaling

### High Availability
- Multi-region deployment
- Firestore replication (automatic)
- Cloud SQL with read replicas
- CDN for frontend (Firebase Hosting/CloudFront)

## Troubleshooting Guide

### Backend won't start
```bash
# Check logs
docker logs api-monitor-backend

# Common fixes:
- Verify .env file exists and is valid
- Check firebase-credentials.json path
- Ensure port 8000 is available
- Verify Python dependencies installed
```

### Health checks failing
```bash
# Test monitor manually
curl -X POST http://localhost:8000/api/monitors/ \
  -H "Authorization: Bearer <token>" \
  -d '{"name":"Test","url":"https://httpbin.org/status/200"}'

# Check scheduler
docker exec api-monitor-backend ps aux | grep python

# View scheduler logs
docker logs api-monitor-backend | grep "scheduler"
```

### Frontend build errors
```bash
# Clear cache
rm -rf node_modules package-lock.json
npm install

# Check Node version
node --version  # Should be 18+

# Build with verbose
npm run build -- --debug
```

## Next Steps After Deployment

1. **Set up monitoring** - Configure uptime checks for the system itself
2. **Enable backups** - Automated database backups
3. **Add notifications** - Email/Slack integration
4. **Create documentation** - User guides
5. **Set up CI/CD** - GitHub Actions
6. **Configure alerts** - CloudWatch/Stackdriver
7. **Performance tuning** - Optimize queries
8. **Security audit** - Regular reviews
9. **Load testing** - Verify scalability
10. **User feedback** - Iterate on features

## Support & Resources

- **Documentation**: See `/docs` directory
- **API Docs**: http://localhost:8000/docs
- **Issues**: GitHub Issues
- **Firebase**: https://firebase.google.com/docs
- **Google Cloud**: https://cloud.google.com/docs
- **FastAPI**: https://fastapi.tiangolo.com
- **React**: https://react.dev

---

**Ready to deploy!** Follow the [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) for step-by-step instructions.
