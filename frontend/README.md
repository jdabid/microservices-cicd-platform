# Frontend - Medical Appointments System

React-based frontend for the Medical Appointments microservices platform.

## 🚀 Quick Start

### Local Development
```bash
npm install
npm run dev
# Visit: http://localhost:3000
```

### Production Build
```bash
npm run build
# Output in dist/
```

### Docker
```bash
# Build
docker build -t microservices-frontend:latest .

# Run
docker run -p 80:80 microservices-frontend:latest

# Visit: http://localhost
```

## 📁 Structure
```
frontend/
├── src/
│   ├── components/
│   │   ├── AppointmentList.jsx
│   │   └── AppointmentForm.jsx
│   ├── App.jsx
│   ├── main.jsx
│   ├── App.css
│   └── index.css
├── public/
├── index.html
├── vite.config.js
├── package.json
├── Dockerfile
└── nginx.conf
```

## 🔧 Tech Stack

- **Framework:** React 18.2.0
- **Build Tool:** Vite 5.0.11
- **HTTP Client:** Axios 1.6.5
- **Runtime:** Nginx 1.25-alpine
- **Image Size:** ~45MB

## 📊 Features

- Create appointments with validation
- List appointments with status badges
- Real-time API health monitoring
- Responsive design (mobile/desktop)
- Form error handling
- Loading states

## 🐳 Docker Details

**Multi-stage build:**
1. Builder: Node 20 Alpine (install deps + build)
2. Runtime: Nginx Alpine (serve static files)

**Security:**
- Non-root user (nginxuser, UID 1000)
- Security headers configured
- Health checks enabled

**Nginx proxy:**
- `/api/*` → Backend API
- `/health` → Backend health endpoint
- SPA routing with try_files

## 🔗 Links

- Frontend: http://localhost (port 80)
- API (proxied): http://localhost/api
- Backend (direct): http://localhost:8000