# 🔍 API Monitor System

A production-ready, real-time API monitoring and alerting system built with FastAPI, React, Firebase, and Google Cloud.
![Dashboard](https://github.com/Pu5hk4r/API-Monitor-Analytics/blob/main/APIMonitorAnalytics_dashboard.png)
![ALert1](https://github.com/Pu5hk4r/API-Monitor-Analytics/blob/main/APIMonitorAnalytics_Monitors.png)
![Alert2](https://github.com/Pu5hk4r/API-Monitor-Analytics/blob/main/API_Monitor_mini.png)

![Architecture](https://img.shields.io/badge/Architecture-Microservices-blue)
![Python](https://img.shields.io/badge/Python-3.11-green)
![React](https://img.shields.io/badge/React-18.2-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🌟 Features

### Core Monitoring
- ✅ **Real-time API Health Checks** - Monitor any HTTP/HTTPS endpoint every 5 minutes
- 📊 **Comprehensive Metrics** - Track uptime, response times (p50, p95, p99), error rates
- 🚨 **Intelligent Alerts** - AI-powered error analysis using Google Gemini
- 📈 **Historical Data** - 7-day retention with time-series analysis
- 🎯 **Custom Configurations** - Per-monitor settings for intervals, timeouts, and expected responses

### Technical Features
- 🔐 **Firebase Authentication** - Secure user management
- 🗄️ **Firestore Database** - Scalable NoSQL for monitor configs
- 💾 **SQLite Time-Series** - Efficient local metrics storage
- 🐳 **Docker Containerized** - Easy deployment with Docker Compose
- 🔒 **Production-Ready Security** - HTTPS, CORS, rate limiting, security headers
- 🎨 **Modern UI** - React with Tailwind CSS and Chart.js
- 🤖 **AI Analysis** - Gemini-powered error diagnostics
- 📦 **In-Memory Caching** - 5-minute TTL for performance

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    USERS (Web Browser)                           │
│              https://monitor.yourdomain.com                      │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTPS (443)
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│            S3 + CloudFront (Static Frontend)                     │
│                   React SPA Application                          │
└───────────────────────────┬─────────────────────────────────────┘
                            │ REST API + Firebase Auth
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                 AWS EC2 / Google Compute Engine                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Nginx (Reverse Proxy)                                    │  │
│  │  • SSL/TLS Termination                                    │  │
│  │  • Rate Limiting (100 req/min)                            │  │
│  └────────────────┬─────────────────────────────────────────┘  │
│                   │ proxy_pass                                   │
│  ┌────────────────▼─────────────────────────────────────────┐  │
│  │  FastAPI Backend + APScheduler                            │  │
│  │  • REST API (8000)                                        │  │
│  │  • Background Workers                                     │  │
│  │  • SQLite Database                                        │  │
│  │  • In-Memory Cache                                        │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                            │
      ┌─────────────────────┼─────────────────────┐
      ▼                     ▼                     ▼
┌──────────┐          ┌──────────┐         ┌──────────┐
│ Firebase │          │  Gemini  │         │   GCP    │
│ Auth &   │          │   API    │         │ Logging  │
│ Firestore│          │    AI    │         │          │
└──────────┘          └──────────┘         └──────────┘
```

## 📁 Project Structure

```
api-monitor-system/
├── backend/                    # FastAPI Backend
│   ├── main.py                # Application entry point
│   ├── app/
│   │   ├── core/              # Core configurations
│   │   │   ├── config.py      # Settings & environment
│   │   │   └── firebase.py    # Firebase integration
│   │   ├── database/          # Database layer
│   │   │   └── sqlite_db.py   # SQLite operations
│   │   ├── models/            # Pydantic schemas
│   │   │   └── schemas.py     # Request/response models
│   │   ├── routers/           # API endpoints
│   │   │   ├── monitors.py    # Monitor CRUD
│   │   │   ├── metrics.py     # Metrics endpoints
│   │   │   ├── alerts.py      # Alert endpoints
│   │   │   └── auth.py        # Authentication
│   │   ├── scheduler/         # Background jobs
│   │   │   └── monitor_scheduler.py
│   │   └── services/          # Business logic
│   │       ├── monitor_checker.py
│   │       ├── gemini_service.py
│   │       └── cache_service.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── frontend/                   # React Frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/             # Page components
│   │   ├── services/          # API clients
│   │   ├── context/           # React context
│   │   ├── config/            # Configuration
│   │   └── utils/             # Utilities
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
├── infrastructure/             # Deployment configs
│   ├── docker-compose.yml
│   ├── nginx/
│   │   ├── nginx.conf
│   │   └── conf.d/
│   └── scripts/
└── docs/                       # Documentation
    ├── DEPLOYMENT_GUIDE.md    # Deployment instructions
    ├── API_REFERENCE.md       # API documentation
    └── ARCHITECTURE.md        # System architecture
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Google Cloud account
- Firebase project

### 1. Clone Repository

```bash
git clone <repository-url>
cd api-monitor-system
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Place Firebase credentials
mkdir secrets
cp /path/to/firebase-credentials.json secrets/

# Run development server
python main.py
```

Backend will be available at http://localhost:8000

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Add Firebase configuration

# Run development server
npm run dev
```

Frontend will be available at http://localhost:3000

### 4. Docker Compose (Recommended)

```bash
cd infrastructure

# Configure environment
cp ../.env.example .env
# Edit with your credentials

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 📊 API Endpoints

### Authentication
- `GET /api/auth/me` - Get current user
- `GET /api/auth/verify` - Verify token

### Monitors
- `GET /api/monitors/` - List all monitors
- `GET /api/monitors/{id}` - Get monitor details
- `POST /api/monitors/` - Create monitor
- `PUT /api/monitors/{id}` - Update monitor
- `DELETE /api/monitors/{id}` - Delete monitor
- `GET /api/monitors/{id}/health-checks` - Get health history
- `GET /api/monitors/dashboard/stats` - Dashboard statistics

### Metrics
- `GET /api/metrics/{id}?hours=24` - Get monitor metrics
- `GET /api/metrics/{id}/daily?days=7` - Get daily metrics

### Alerts
- `GET /api/alerts/{monitor_id}` - Get monitor alerts
- `GET /api/alerts/` - Get all user alerts

### Health
- `GET /health` - System health check

Full API documentation: http://localhost:8000/docs

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
# Firebase
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_CREDENTIALS_PATH=/app/secrets/firebase-credentials.json

# Google Cloud
GCP_PROJECT_ID=your-gcp-project-id
GEMINI_API_KEY=your-gemini-api-key

# Database
SQLITE_DB_PATH=/app/database/metrics.db
DATA_RETENTION_DAYS=7

# Monitoring
MONITOR_CHECK_INTERVAL_MINUTES=5
MAX_WORKERS=10
REQUEST_TIMEOUT_SECONDS=30

# Security
ALLOWED_ORIGINS=["http://localhost:3000"]
RATE_LIMIT_PER_MINUTE=100

# Alerts
MAX_CONSECUTIVE_FAILURES=3
ALERT_COOLDOWN_MINUTES=30
```

#### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
VITE_FIREBASE_API_KEY=your-api-key
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
VITE_FIREBASE_APP_ID=your-app-id
```

## 🔐 Security Features

- **Firebase Authentication** - Industry-standard auth
- **HTTPS Only** - TLS 1.2+ encryption
- **CORS Protection** - Whitelist-based origins
- **Rate Limiting** - 100 requests/minute per IP
- **Security Headers** - XSS, clickjacking protection
- **Input Validation** - Pydantic schemas
- **SQL Injection Prevention** - Parameterized queries
- **Token Verification** - Firebase ID token validation

## 📈 Performance

- **Response Time**: < 100ms (API endpoints)
- **Monitoring Interval**: 5 minutes (configurable)
- **Cache TTL**: 5 minutes
- **Data Retention**: 7 days (configurable)
- **Concurrent Checks**: 10 workers
- **Database**: SQLite (for single instance) or Cloud SQL (for scale)

## 🎯 Use Cases

1. **Production API Monitoring** - Monitor critical APIs
2. **SLA Compliance** - Track and report uptime
3. **Performance Analysis** - Identify slow endpoints
4. **Incident Response** - AI-powered error diagnosis
5. **Multi-Environment** - Monitor dev, staging, production
6. **Third-Party Services** - Track external dependencies

## 📝 Example Monitor Configuration

```json
{
  "name": "Production API",
  "url": "https://api.example.com/health",
  "method": "GET",
  "headers": {
    "Authorization": "Bearer token123"
  },
  "interval_minutes": 5,
  "timeout_seconds": 30,
  "expected_status_code": 200,
  "alert_on_failure": true,
  "alert_threshold_minutes": 15
}
```

## 🔍 Monitoring Dashboard Features

- **Real-time Status** - Live monitor status
- **Uptime Percentage** - 24-hour rolling window
- **Response Time Charts** - P50, P95, P99 percentiles
- **Alert History** - Recent incidents
- **AI Analysis** - Gemini-powered insights
- **Export Data** - CSV/JSON exports

## 🛠️ Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code Quality

```bash
# Python linting
flake8 backend/
black backend/

# JavaScript linting
cd frontend
npm run lint
```

## 📚 Documentation

- [Deployment Guide](docs/DEPLOYMENT_GUIDE.md) - Complete deployment instructions
- [API Reference](docs/API_REFERENCE.md) - Detailed API documentation
- [Architecture](docs/ARCHITECTURE.md) - System design details

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)
- **Email**: support@yourdomain.com

## 🙏 Acknowledgments

- FastAPI - Modern Python web framework
- React - UI library
- Firebase - Authentication and database
- Google Cloud - Infrastructure
- Gemini AI - Error analysis
- Tailwind CSS - Styling framework
- Chart.js - Data visualization

## 🔮 Future Enhancements

- [ ] Multi-region monitoring
- [ ] Webhook notifications
- [ ] Custom dashboards
- [ ] API rate limit monitoring
- [ ] SSL certificate expiry alerts
- [ ] Mobile app
- [ ] Slack/Discord integration
- [ ] Advanced analytics
- [ ] Team collaboration features
- [ ] SLA reporting

---

**Built with ❤️ using FastAPI, React, Firebase, and Google Cloud**

**Version**: 1.0.0
**Last Updated**: February 2024
