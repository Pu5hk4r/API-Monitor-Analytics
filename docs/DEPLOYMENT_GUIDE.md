# API Monitor System - Complete Deployment Guide

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Google Cloud Setup](#google-cloud-setup)
3. [Firebase Configuration](#firebase-configuration)
4. [Backend Deployment](#backend-deployment)
5. [Frontend Deployment](#frontend-deployment)
6. [Production Deployment](#production-deployment)
7. [Monitoring & Maintenance](#monitoring--maintenance)

---

## Prerequisites

### Required Tools
- Google Cloud Platform account
- Firebase project
- Node.js 18+ and npm
- Python 3.11+
- Docker and Docker Compose
- Git

### Required API Keys
- Firebase Admin SDK credentials
- Gemini API key
- Google Cloud credentials

---

## Google Cloud Setup

### 1. Create Google Cloud Project

```bash
# Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init

# Create new project
gcloud projects create api-monitor-system --name="API Monitor System"
gcloud config set project api-monitor-system

# Enable required APIs
gcloud services enable compute.googleapis.com
gcloud services enable logging.googleapis.com
gcloud services enable aiplatform.googleapis.com
```

### 2. Get Gemini API Key

1. Go to Google AI Studio: https://makersuite.google.com/app/apikey
2. Create API key
3. Save for later use

### 3. Create Service Account

```bash
# Create service account
gcloud iam service-accounts create api-monitor-sa \
    --display-name="API Monitor Service Account"

# Get service account email
SA_EMAIL=$(gcloud iam service-accounts list \
    --filter="displayName:API Monitor Service Account" \
    --format='value(email)')

# Grant necessary roles
gcloud projects add-iam-policy-binding api-monitor-system \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/logging.logWriter"

# Create and download key
gcloud iam service-accounts keys create ~/api-monitor-key.json \
    --iam-account=${SA_EMAIL}
```

---

## Firebase Configuration

### 1. Create Firebase Project

1. Go to Firebase Console: https://console.firebase.google.com
2. Click "Add project"
3. Select your Google Cloud project or create new
4. Enable Google Analytics (optional)

### 2. Enable Firebase Authentication

1. In Firebase Console, go to Authentication
2. Click "Get Started"
3. Enable Email/Password authentication
4. (Optional) Enable Google Sign-In

### 3. Create Firestore Database

1. Go to Firestore Database
2. Click "Create database"
3. Start in production mode
4. Choose location (choose closest to your users)

### 4. Set Up Firestore Security Rules

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users collection
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Monitors collection
    match /monitors/{monitorId} {
      allow read, write: if request.auth != null && 
                          resource.data.user_id == request.auth.uid;
      allow create: if request.auth != null;
    }
    
    // Alerts collection
    match /alerts/{alertId} {
      allow read: if request.auth != null && 
                   resource.data.user_id == request.auth.uid;
      allow write: if false; // Only backend can write alerts
    }
  }
}
```

### 5. Get Firebase Config

1. Go to Project Settings > General
2. Under "Your apps", click web icon (</>)
3. Register app with nickname "API Monitor"
4. Copy config object

### 6. Download Firebase Admin SDK Key

1. Go to Project Settings > Service Accounts
2. Click "Generate new private key"
3. Save as `firebase-credentials.json`

---

## Backend Deployment

### 1. Clone and Configure

```bash
# Clone repository
cd /home/claude/api-monitor-system

# Configure environment
cd backend
cp .env.example .env

# Edit .env file
nano .env
```

Add your credentials:
```env
FIREBASE_PROJECT_ID=your-project-id
GCP_PROJECT_ID=your-gcp-project-id
GEMINI_API_KEY=your-gemini-api-key
ALLOWED_ORIGINS=["https://monitor.yourdomain.com"]
```

### 2. Local Development

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Place firebase credentials
mkdir -p secrets
cp ~/firebase-credentials.json secrets/

# Run development server
python main.py
```

Server will start at http://localhost:8000

### 3. Test Backend

```bash
# Health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/docs
```

---

## Frontend Deployment

### 1. Configure Frontend

```bash
cd frontend

# Install dependencies
npm install

# Create Firebase config
```

Create `src/config/firebase.js`:
```javascript
import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';

const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_PROJECT.firebaseapp.com",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_PROJECT.appspot.com",
  messagingSenderId: "YOUR_SENDER_ID",
  appId: "YOUR_APP_ID"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app);
```

### 2. Development Server

```bash
npm run dev
```

Application will start at http://localhost:3000

### 3. Build for Production

```bash
npm run build
```

Output will be in `dist/` directory

---

## Production Deployment

### Option 1: Google Compute Engine VM

#### 1. Create VM Instance

```bash
# Create VM
gcloud compute instances create api-monitor-vm \
    --zone=us-central1-a \
    --machine-type=e2-medium \
    --boot-disk-size=30GB \
    --boot-disk-type=pd-standard \
    --image-family=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud \
    --tags=http-server,https-server

# Configure firewall
gcloud compute firewall-rules create allow-http \
    --allow=tcp:80 \
    --target-tags=http-server

gcloud compute firewall-rules create allow-https \
    --allow=tcp:443 \
    --target-tags=https-server
```

#### 2. SSH and Setup

```bash
# SSH into VM
gcloud compute ssh api-monitor-vm --zone=us-central1-a

# Install Docker
sudo apt update
sudo apt install -y docker.io docker-compose
sudo usermod -aG docker $USER

# Install Git
sudo apt install -y git

# Clone repository
git clone <your-repo-url>
cd api-monitor-system
```

#### 3. Deploy with Docker Compose

```bash
# Copy environment file
cp backend/.env.example backend/.env
nano backend/.env  # Add your credentials

# Copy Firebase credentials
sudo mkdir -p /var/lib/firebase
sudo cp firebase-credentials.json /var/lib/firebase/

# Update docker-compose.yml volume path
# Change firebase_secrets volume to:
#   firebase_secrets:
#     driver: local
#     driver_opts:
#       type: none
#       o: bind
#       device: /var/lib/firebase

# Start services
cd infrastructure
sudo docker-compose up -d

# Check logs
sudo docker-compose logs -f
```

#### 4. Setup SSL with Let's Encrypt

```bash
# First-time certificate generation
sudo docker-compose run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email your-email@example.com \
    --agree-tos \
    --no-eff-email \
    -d api.yourdomain.com

# Restart nginx
sudo docker-compose restart nginx
```

### Option 2: Google Cloud Run (Serverless)

#### 1. Build and Push Container

```bash
# Configure Docker for GCP
gcloud auth configure-docker

# Build backend image
cd backend
docker build -t gcr.io/api-monitor-system/backend:latest .

# Push to Container Registry
docker push gcr.io/api-monitor-system/backend:latest
```

#### 2. Deploy to Cloud Run

```bash
# Deploy service
gcloud run deploy api-monitor-backend \
    --image gcr.io/api-monitor-system/backend:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars="FIREBASE_PROJECT_ID=your-project" \
    --set-env-vars="GEMINI_API_KEY=your-key" \
    --max-instances=10 \
    --memory=512Mi
```

**Note**: Cloud Run is stateless, so you'll need Cloud SQL or Firestore for persistence instead of SQLite.

### Option 3: Frontend on Firebase Hosting

```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login
firebase login

# Initialize Firebase
cd frontend
firebase init hosting

# Build production bundle
npm run build

# Deploy
firebase deploy --only hosting
```

---

## Environment-Specific Configuration

### Development (.env.development)
```env
DEBUG=True
ALLOWED_ORIGINS=["http://localhost:3000"]
MONITOR_CHECK_INTERVAL_MINUTES=1
```

### Production (.env.production)
```env
DEBUG=False
ALLOWED_ORIGINS=["https://monitor.yourdomain.com"]
MONITOR_CHECK_INTERVAL_MINUTES=5
```

---

## Monitoring & Maintenance

### 1. View Logs

```bash
# Docker logs
sudo docker-compose logs -f backend
sudo docker-compose logs -f nginx

# Google Cloud Logging
gcloud logging read "resource.type=gce_instance" --limit 50
```

### 2. Database Maintenance

```bash
# Backup SQLite database
sudo docker exec api-monitor-backend \
    sqlite3 /app/database/metrics.db ".backup '/app/database/backup.db'"

# Copy backup to host
sudo docker cp api-monitor-backend:/app/database/backup.db ./backup.db
```

### 3. Update Application

```bash
# Pull latest code
git pull

# Rebuild and restart
cd infrastructure
sudo docker-compose build
sudo docker-compose up -d

# Clean up old images
sudo docker system prune -a
```

### 4. Monitor Resources

```bash
# Check container stats
sudo docker stats

# Check disk usage
df -h
sudo docker system df

# Check memory
free -h
```

---

## Troubleshooting

### Backend won't start
```bash
# Check logs
sudo docker-compose logs backend

# Common issues:
# 1. Missing environment variables
# 2. Firebase credentials not mounted
# 3. Port already in use
```

### Can't connect to Firestore
```bash
# Verify credentials
sudo docker exec api-monitor-backend \
    cat /app/secrets/firebase-credentials.json

# Check network
sudo docker exec api-monitor-backend ping -c 3 firestore.googleapis.com
```

### SSL certificate issues
```bash
# Regenerate certificate
sudo docker-compose run --rm certbot certonly --webroot \
    --webroot-path=/var/www/certbot \
    -d api.yourdomain.com --force-renewal

# Restart nginx
sudo docker-compose restart nginx
```

---

## Security Checklist

- [ ] Change default passwords
- [ ] Configure Firestore security rules
- [ ] Enable HTTPS only
- [ ] Set up rate limiting
- [ ] Configure CORS properly
- [ ] Enable Cloud Armor (DDoS protection)
- [ ] Regular security updates
- [ ] Monitor access logs
- [ ] Implement backup strategy
- [ ] Set up alerting for errors

---

## Cost Optimization

### Free Tier Limits
- **Firestore**: 50K reads/day, 20K writes/day
- **Gemini**: 60 requests/minute
- **Cloud Run**: 2 million requests/month
- **Compute Engine**: Use e2-micro (free tier)

### Tips
1. Use Cloud Run instead of always-on VM when possible
2. Implement aggressive caching
3. Set up Cloud Scheduler to stop/start VM during off-hours
4. Use preemptible VMs for development
5. Monitor billing alerts

---

## Next Steps

1. **Set up monitoring**: Configure Cloud Monitoring dashboards
2. **Add notifications**: Integrate with Slack/Discord/Email
3. **Enable backups**: Automated database backups
4. **CI/CD pipeline**: GitHub Actions or Cloud Build
5. **Multi-region deployment**: For better availability

---

## Support Resources

- [Firebase Documentation](https://firebase.google.com/docs)
- [Google Cloud Documentation](https://cloud.google.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [React Documentation](https://react.dev)
- [Gemini API Documentation](https://ai.google.dev/docs)

---

**Version**: 1.0.0
**Last Updated**: 2024-02-10
