# Yeet Bank Backend

A Django REST API backend for the Yeet Bank application - a simulation banking platform.

## Features

- ✅ User registration and authentication (JWT)
- ✅ Multi-method login (Email, Phone, Account Number)
- ✅ User profiles with banking information
- ✅ Transaction management (Deposits, Withdrawals, Transfers, Payments)
- ✅ Real-time notifications via WebSocket
- ✅ Account balance management
- ✅ Admin interface for user and transaction management

## Tech Stack

- **Django 5.1** - Web framework
- **Django REST Framework** - API development
- **Django Channels** - WebSocket support
- **JWT Authentication** - Token-based auth
- **PostgreSQL/SQLite** - Database
- **CORS** - Cross-origin support

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `POST /api/auth/token/refresh/` - Refresh JWT token

### User Management
- `GET /api/user/profile/` - Get user profile
- `PUT /api/user/profile/` - Update user profile

### Transactions
- `GET /api/transactions/` - List user transactions
- `POST /api/transactions/create/` - Create new transaction
- `GET /api/transactions/recent/` - Get recent transactions

### Notifications
- `GET /api/notifications/` - List user notifications
- `GET /api/notifications/{id}/` - Get specific notification
- `POST /api/notifications/mark-all-read/` - Mark all notifications as read

### WebSocket
- `ws/notifications/` - Real-time notifications

## Setup

1. **Clone and navigate to backend directory**
   ```bash
   cd yeet-bank/backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start development server**
   ```bash
   python manage.py runserver
   ```

## Testing

Run the test script to verify API functionality:
```bash
python test_api.py
```

## Project Structure

```
backend/
├── yeet_bank/              # Main Django project
│   ├── settings.py        # Django settings
│   ├── urls.py           # Main URL configuration
│   ├── asgi.py           # ASGI configuration for WebSockets
│   └── wsgi.py           # WSGI configuration
├── accounts/              # User management app
│   ├── models.py         # User model
│   ├── views.py          # API views
│   ├── serializers.py    # Data serializers
│   └── urls.py           # URL patterns
├── transactions/          # Transaction management app
│   ├── models.py         # Transaction model
│   ├── views.py          # Transaction views
│   ├── serializers.py    # Transaction serializers
│   └── urls.py           # Transaction URLs
├── notifications/         # Notification system
│   ├── models.py         # Notification model
│   ├── views.py          # Notification views
│   ├── consumers.py      # WebSocket consumers
│   ├── routing.py        # WebSocket routing
│   └── signals.py        # Django signals
├── manage.py             # Django management script
├── requirements.txt      # Python dependencies
├── .env.example          # Environment template
└── test_api.py           # API test script
```

## Database Models

### User (accounts.User)
- Extends Django's AbstractUser
- Additional fields: phone, country, residential_address, account_number, balance, is_verified

### Transaction (transactions.Transaction)
- Fields: transaction_id, type, amount, description, status, sender, recipient, recipient_account

### Notification (notifications.Notification)
- Fields: user, title, message, type, is_read, is_active

## Security Features

- JWT token authentication
- Password validation (8+ characters)
- Account number generation
- Balance validation for transactions
- CORS configuration
- CSRF protection

## Development

- **Admin Interface**: `/admin/` - Django admin panel
- **API Documentation**: Available at `/api/` endpoints
- **WebSocket Testing**: Use tools like WebSocket King for testing real-time features

## Production Deployment

For production deployment:
1. Set `DEBUG = False` in settings
2. Use PostgreSQL database
3. Configure proper SECRET_KEY
4. Set up Redis for Channels
5. Configure email settings
6. Use a production ASGI server (Daphne)

## License

Educational Use - See main project README for details.