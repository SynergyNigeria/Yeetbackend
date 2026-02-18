# 🕒🏦 Yeet - Yesterday Bank App

**A practical, full-stack banking simulation application** built to demonstrate real-world digital banking workflows. Yeet is a Progressive Web App (PWA) that simulates core banking operations using demo tokens instead of real currency, designed for learning, testing, and portfolio purposes.

[![License](https://img.shields.io/badge/License-Educational%20Use-blue.svg)](LICENSE)
[![Tech Stack](https://img.shields.io/badge/Stack-Django%20%26%20React-brightgreen.svg)](README.md)
[![Status](https://img.shields.io/badge/Status-In%20Development-yellow.svg)](README.md)

---

## 🎯 Project Vision

Yeet bridges the gap between **theoretical banking knowledge** and **practical full-stack development**. It demonstrates:

- ✅ Secure user authentication and session management
- ✅ Multi-layer account verification and transfer controls
- ✅ Real-time WebSocket communication
- ✅ Scalable RESTful API architecture
- ✅ Progressive Web App capabilities
- ✅ Email notifications and push alerts
- ✅ Role-based access control

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **Node.js 18+** and **npm**
- **PostgreSQL 12+** (or SQLite for development)
- **Git**

### Backend Setup

```bash
# Clone the repository
git clone <repository-url>
cd yeet bank/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your database credentials and settings

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

### Frontend Setup

```bash
cd yeet bank/frontend

# Install dependencies
npm install

# Configure environment variables
cp .env.example .env
# Update API endpoint in .env

# Start development server
npm start
```

---

## 🧱 Tech Stack

### Backend

| Technology | Purpose |
|-----------|---------|
| **Django 4.x** | Web framework |
| **Django REST Framework** | API development |
| **Django Channels** | WebSocket support for real-time chat & notifications |
| **PostgreSQL** | Primary database (SQLite for dev) |
| **JWT (PyJWT)** | Token-based authentication |
| **Celery** | Async task queue for emails & notifications |
| **Django-CORS** | Cross-Origin Resource Sharing |

### Frontend

| Technology | Purpose |
|-----------|---------|
| **React 18** | UI framework |
| **Tailwind CSS** | Utility-first styling |
| **Feather Icons** | Icon library |
| **Axios** | HTTP client |
| **Socket.io** | Real-time communication |
| **Workbox** | PWA service worker management |

### Infrastructure & Tools

- **PostgreSQL** / **Redis** (caching & WebSocket support)
- **Docker** (optional containerization)
- **Nginx** (production reverse proxy)
- **Gunicorn** (production WSGI server)

---

## 📱 Core Features

### 1️⃣ User Authentication & Accounts

Users can authenticate using:
- Account Number
- Email Address
- Phone Number

**JWT-based session handling** ensures secure API access.

Each account automatically includes:
- Unique account number
- Default transfer PIN (user-changeable)
- Account level assignments

---

### 2️⃣ User Registration & Onboarding

Comprehensive registration with:
- Personal information (name, email, phone)
- Location details (country, residential address)
- Secure password setup
- **Required email verification**
- Automated welcome email

```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "phone": "+234801234567",
  "country": "Nigeria",
  "residential_address": "123 Main St",
  "password": "SecurePassword123!"
}
```

---

### 3️⃣ Account Levels & Verification Checks

Transfers are controlled by **multiple verification checks** that simulate real banking restrictions:

#### Account Status Flags

| Flag | Purpose |
|------|---------|
| `is_verified` | Basic email/phone verification |
| `has_deposit` | User has made initial deposit |
| `is_basic` | Basic account tier |
| `is_premium` | Premium tier with higher limits |
| `is_business` | Business account features |
| **`is_prime`** | **Tier 0 - Bypasses all checks** |

#### Prime Account Privileges

When `is_prime = true`:
- ✅ **All transfer checks are bypassed**
- ✅ No account level restrictions apply
- ✅ Represents specially approved or top-tier accounts
- ✅ Transfers succeed immediately

---

### 4️⃣ Internal Token Transfers

Send demo tokens between registered users:

```json
{
  "recipient_account_number": "ACC0001234",
  "amount": 5000,
  "transfer_pin": "1234",
  "message": "Lunch payment"
}
```

**Requirements:**
- Valid recipient account
- Correct transfer PIN
- All required account checks passed
- Sufficient balance

**Response includes:**
- Transaction status (success/pending/failed)
- Transaction ID
- Timestamp
- Error reason (if failed)

---

### 5️⃣ External Transfers

Send tokens to simulated external accounts:
- Uses **identical validation** as internal transfers
- Mimics real bank outbound transfers
- Includes processing fee simulation

---

### 6️⃣ Deposits (Support Chat Integration)

**Users cannot self-deposit tokens.** Instead:

1. User initiates deposit request
2. Pre-filled chat message sent to support
3. Customer service manually processes deposit
4. User notified via email + push notification

This approach:
- 📩 Simulates manual bank funding
- 💬 Encourages support chat usage
- 🔐 Adds verification layer
- 📊 Creates support ticket trail

---

### 7️⃣ Notifications System

#### Email Notifications

Users receive emails for:
- 📧 Account verification
- 👋 Welcome message (post-signup)
- 🔐 Login alerts
- 💰 Incoming transaction alerts
- 🔔 Custom admin announcements

#### In-App & Push Notifications

- 📲 Push notifications for installed PWA
- 💬 New chat messages
- 📈 Transaction status updates
- 📢 Admin announcements
- ⏰ Support response reminders

---

### 8️⃣ Real-Time Customer Support Chat

**WebSocket-powered live chat** between users and support:

Features:
- ⚡ Instant message delivery
- 📱 Mobile push notifications
- ⏰ Unread message indicators
- ⏱️ Idle timeout reminders
- 📎 Message history

Admin capabilities:
- View all active chats
- Assign conversations to agents
- Send canned responses
- Escalation workflows

---

### 9️⃣ Admin Dashboard

**Comprehensive admin panel** for system management:

**User Management:**
- View all users & accounts
- Edit account levels
- Toggle verification checks
- Suspend/reactivate accounts
- Force password reset

**Transaction Monitoring:**
- Real-time transaction logs
- Filter by date, user, type
- Dispute resolution
- Transaction reversal (if needed)

**Notifications:**
- Send custom email alerts
- Broadcast in-app notifications
- Schedule announcements

**Support Management:**
- Chat monitoring
- Agent assignments
- Performance metrics
- Audit logs

---

## 🔐 Security Architecture

### Authentication & Authorization

```
User Login
    ↓
Credential Verification (email/phone/account#)
    ↓
Password Hash Validation (bcrypt)
    ↓
JWT Token Generation (access + refresh)
    ↓
WebSocket Auth (token in headers)
    ↓
Role-Based Access Control (RBAC)
```

### Transaction Security

- **Transfer PIN requirement** for sensitive operations
- **Multi-layer verification checks** before transfer approval
- **Rate limiting** on API endpoints
- **Account activity logs** for audit trails
- **HTTPS enforcement** in production
- **CORS validation** for cross-origin requests

### Data Protection

- 🔒 Passwords hashed with bcrypt (salt rounds: 12)
- 🔐 Transfer PINs hashed separately
- 🛡️ JWT tokens with configurable expiration
- 📋 Input validation on all endpoints
- 🚫 SQL injection prevention (ORM usage)
- 🔑 Environment-based secrets (no hardcoded credentials)

---

## 📦 Progressive Web App (PWA)

Yeet is a **fully-featured PWA** with:

| Feature | Description |
|---------|-------------|
| **Installability** | Add to home screen on mobile/desktop |
| **Offline Support** | Critical pages available offline |
| **Push Notifications** | Real-time alerts via Web Push API |
| **App Shell** | Fast loading with cached shell strategy |
| **Mobile Responsive** | Optimized for all screen sizes |
| **App-like UX** | Full-screen mode, custom status bar |

### Installation

1. Visit app in modern browser
2. Install prompt appears (or via menu)
3. App added to home screen
4. Launch like native app

### Service Worker Strategy

```
Network First (Chat/Transactions)
    ↓ Fallback to cache if offline
    
Cache First (Static Assets)
    ↓ Network update in background
    
Stale While Revalidate (User Data)
```

---

## 🗂️ Project Structure

```
yeet bank/
├── backend/
│   ├── accounts/                 # User auth & profile management
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   └── permissions.py
│   │
│   ├── transactions/             # Transfer & balance logic
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── services.py
│   │   └── validators.py
│   │
│   ├── notifications/            # Email & push notifications
│   │   ├── models.py
│   │   ├── tasks.py
│   │   └── templates/
│   │
│   ├── chat/                     # WebSocket chat system
│   │   ├── models.py
│   │   ├── consumers.py
│   │   └── routing.py
│   │
│   ├── admin_panel/              # Admin dashboard APIs
│   │   ├── views.py
│   │   └── permissions.py
│   │
│   ├── core/                     # Settings, middleware, utils
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── middleware.py
│   │
│   ├── requirements.txt
│   ├── manage.py
│   └── .env.example
│
├── frontend/
│   ├── public/
│   │   ├── index.html
│   │   ├── manifest.json         # PWA manifest
│   │   └── icons/
│   │
│   ├── src/
│   │   ├── components/
│   │   │   ├── Auth/             # Login, Register, Verify
│   │   │   ├── Dashboard/        # Main dashboard
│   │   │   ├── Transactions/     # Transfer forms
│   │   │   ├── Chat/             # Chat interface
│   │   │   ├── Admin/            # Admin-only pages
│   │   │   └── Common/           # Reusable components
│   │   │
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │   ├── Login.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Transfer.jsx
│   │   │   ├── Chat.jsx
│   │   │   └── Admin.jsx
│   │   │
│   │   ├── services/
│   │   │   ├── api.js            # Axios instance
│   │   │   ├── auth.js           # Auth API calls
│   │   │   ├── transactions.js   # Transaction API
│   │   │   ├── chat.js           # WebSocket connection
│   │   │   └── notifications.js  # Push notifications
│   │   │
│   │   ├── hooks/
│   │   │   ├── useAuth.js        # Authentication logic
│   │   │   ├── useBalance.js     # Balance management
│   │   │   ├── useChat.js        # Chat connection
│   │   │   └── useNotifications.js
│   │   │
│   │   ├── context/
│   │   │   ├── AuthContext.js
│   │   │   └── NotificationContext.js
│   │   │
│   │   ├── assets/
│   │   │   ├── styles/           # Tailwind config
│   │   │   └── images/
│   │   │
│   │   └── App.jsx
│   │
│   ├── package.json
│   ├── .env.example
│   └── tailwind.config.js
│
├── docs/                         # Documentation
│   ├── API.md                    # API endpoints
│   ├── SETUP.md                  # Detailed setup guide
│   ├── ARCHITECTURE.md           # System design
│   └── DEPLOYMENT.md             # Production deployment
│
├── docker-compose.yml            # Local development with Docker
├── .gitignore
└── README.md
```

---

## 🔌 API Endpoints Overview

### Authentication Endpoints

```
POST   /api/auth/register/         Create new account
POST   /api/auth/login/            Authenticate user
POST   /api/auth/refresh/          Refresh JWT token
POST   /api/auth/verify-email/     Verify email address
GET    /api/auth/me/               Current user profile
```

### Transaction Endpoints

```
GET    /api/transactions/          List user transactions
POST   /api/transactions/send/     Send internal transfer
POST   /api/transactions/external/ Send external transfer
GET    /api/transactions/{id}/     Get transaction details
```

### Account Endpoints

```
GET    /api/accounts/              Get account details
PUT    /api/accounts/              Update account info
POST   /api/accounts/pin/change/   Change transfer PIN
GET    /api/accounts/balance/      Current balance
```

### Chat Endpoints

```
WebSocket /ws/chat/{room_id}/     Connect to chat room
GET    /api/chat/history/         Get message history
GET    /api/chat/rooms/           List active chats
```

### Admin Endpoints

```
GET    /api/admin/users/          List all users (admin only)
PUT    /api/admin/users/{id}/     Update user account level
POST   /api/admin/alerts/         Send custom alert
GET    /api/admin/transactions/   View all transactions
```

---

## 🧪 Testing Strategy

### Backend Testing

```bash
# Run all tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

**Test Coverage Areas:**
- ✅ Authentication flows
- ✅ Transfer validation & checks
- ✅ Permission enforcement
- ✅ Notification delivery
- ✅ Chat message handling
- ✅ Admin operations

### Frontend Testing

```bash
# Run Jest tests
npm test

# Generate coverage report
npm test -- --coverage
```

---

## 🚀 Deployment Guide

### Production Checklist

- [ ] Set `DEBUG = False` in Django settings
- [ ] Configure allowed hosts
- [ ] Enable HTTPS/SSL certificates
- [ ] Set up PostgreSQL production database
- [ ] Configure Redis for caching
- [ ] Set up email provider (SMTP/SendGrid)
- [ ] Configure Web Push service
- [ ] Run database migrations
- [ ] Collect static files
- [ ] Set up Gunicorn/Nginx
- [ ] Configure environment variables
- [ ] Enable CORS for production domain

### Docker Deployment

```bash
docker-compose -f docker-compose.yml up -d
```

### Environment Variables

```bash
# Backend (.env)
DEBUG=False
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@host:5432/dbname
ALLOWED_HOSTS=yourdomain.com
JWT_SECRET=your-jwt-secret
EMAIL_BACKEND=smtp
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email
EMAIL_HOST_PASSWORD=your-password
REDIS_URL=redis://localhost:6379
CORS_ALLOWED_ORIGINS=https://yourdomain.com

# Frontend (.env)
REACT_APP_API_URL=https://api.yourdomain.com
REACT_APP_WS_URL=wss://api.yourdomain.com
```

---

## 📊 Database Schema Overview

### Key Models

**User Account**
- Account number (unique)
- Email, phone, name
- Location (country, address)
- Password hash
- Transfer PIN hash
- Account level flags

**Transaction**
- Sender/recipient
- Amount
- Type (internal/external)
- Status (pending/success/failed)
- Timestamp
- Reference number

**Chat Message**
- User/support agent
- Room (conversation)
- Message content
- Timestamp
- Read status

**Notification**
- User
- Type (email/push)
- Content
- Status
- Timestamp

---

## 🐛 Troubleshooting

### Common Issues

**Backend won't start:**
```bash
# Check migrations
python manage.py showmigrations

# Apply migrations
python manage.py migrate

# Clear cache
python manage.py clear_cache
```

**Frontend API errors:**
- Verify `.env` has correct `REACT_APP_API_URL`
- Check CORS settings in Django
- Ensure backend server is running

**WebSocket connection fails:**
- Verify Redis is running
- Check Django Channels configuration
- Ensure WebSocket URL uses `wss://` in production

**Email not sending:**
- Test SMTP credentials
- Check firewall/port access
- Verify email provider settings

---

## 🤝 Contributing Guidelines

1. **Fork** the repository
2. **Create** feature branch: `git checkout -b feature/your-feature`
3. **Commit** changes: `git commit -m 'Add your feature'`
4. **Push** to branch: `git push origin feature/your-feature`
5. **Submit** Pull Request

**Code Standards:**
- Follow PEP 8 (Python)
- Follow Airbnb style guide (JavaScript)
- Write tests for new features
- Update documentation

---

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [React Documentation](https://react.dev/)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [Django Channels Guide](https://channels.readthedocs.io/)
- [PWA Documentation](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps)

---

## 📄 License

This project is open for **educational and portfolio use**. Feel free to explore, modify, and learn from it.

---

## 👤 Author

**Chukwudi Valentine**

A practical full-stack banking simulation demonstrating real-world digital banking workflows using Django and React.

---

## 📞 Support

For issues, questions, or suggestions:
- 📧 Open an issue on GitHub
- 💬 Check existing discussions
- 📚 Review documentation

---

**Last Updated:** February 2026 | **Status:** Active Development

