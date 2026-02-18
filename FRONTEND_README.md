# Yeet Bank Frontend Documentation

This document outlines all the frontend pages, components, and API endpoints required to build the backend for Yeet Bank.

## 🏗️ Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   ├── pages/              # Main application pages
│   ├── context/            # React context providers
│   ├── services/           # API service functions
│   ├── constants/          # Application constants
│   └── assets/             # Static assets
```

## 📱 Pages & Functionality

### 1. Authentication Pages

#### **Login Page** (`/login`)
**File:** `src/pages/Login.jsx`

**Features:**
- Multi-method login (Email, Phone, Account Number)
- Password visibility toggle
- Demo credentials display
- Form validation
- Loading states

**API Calls Needed:**
```javascript
POST /api/auth/login/
{
  "identifier": "email|phone|account_number",
  "password": "string"
}
Response: {
  "access": "jwt_token",
  "refresh": "jwt_token",
  "user": { /* user object */ }
}
```

#### **Register Page** (`/register`)
**File:** `src/pages/Register.jsx`

**Features:**
- User registration form
- Email verification flow
- Form validation
- Terms acceptance

**API Calls Needed:**
```javascript
POST /api/auth/register/
{
  "first_name": "string",
  "last_name": "string",
  "email": "string",
  "phone": "string",
  "country": "string",
  "residential_address": "string",
  "password": "string"
}
Response: {
  "id": "number",
  "email": "string",
  "account_number": "string",
  "message": "string"
}
```

### 2. Main Application Pages

#### **Dashboard** (`/dashboard`)
**File:** `src/pages/Dashboard.jsx`

**Features:**
- Account balance display (with hide/show toggle)
- Recent transactions list
- Quick actions (Send Money, Settings, Add Money)
- Notifications system (full-page view)
- Transfer type selection popup
- Add money popup (with simulated error flow)
- Account information display

**API Calls Needed:**
```javascript
GET /api/user/profile/          # Get user profile & balance
GET /api/transactions/recent/   # Get recent transactions (limit: 4-5)
GET /api/notifications/         # Get user notifications
POST /api/auth/logout/          # Logout endpoint
```

**Data Structures:**
```javascript
// User Profile
{
  "id": "number",
  "first_name": "string",
  "last_name": "string",
  "email": "string",
  "phone": "string",
  "account_number": "string",
  "balance": "number",
  "is_verified": "boolean",
  "is_admin": "boolean"
}

// Recent Transactions
[{
  "id": "number",
  "type": "received|sent",
  "user": "string",
  "amount": "number",
  "date": "string",
  "status": "completed|pending|failed",
  "message": "string"
}]

// Notifications
[{
  "id": "number",
  "type": "transaction|security|system",
  "title": "string",
  "message": "string",
  "time": "string",
  "read": "boolean"
}]
```

#### **Yeet Transfer** (`/yeet-transfer`)
**File:** `src/pages/YeetTransfer.jsx`

**Features:**
- 3-step transfer process:
  1. Account lookup (10-digit account number)
  2. Amount entry & confirmation
  3. PIN verification (onscreen keypad)
- Receiver validation
- Balance checking
- Transfer success confirmation

**API Calls Needed:**
```javascript
POST /api/transfers/validate-receiver/
{
  "account_number": "string"  // 10 digits
}
Response: {
  "name": "string",
  "email": "string"
}

POST /api/transfers/yeet-transfer/
{
  "receiver_account": "string",
  "amount": "number",
  "pin": "string"  // 4 digits
}
Response: {
  "success": "boolean",
  "transaction_id": "string",
  "message": "string"
}
```

#### **Wire Transfer** (`/wire-transfer`)
**File:** `src/pages/WireTransfer.jsx`

**Features:**
- 3-step external bank transfer:
  1. Recipient details (name, bank, account, IFSC)
  2. Amount & description
  3. PIN verification
- External bank validation
- Transfer fee calculation ($25)

**API Calls Needed:**
```javascript
POST /api/transfers/validate-ifsc/
{
  "ifsc_code": "string"
}
Response: {
  "bank_name": "string",
  "branch": "string",
  "valid": "boolean"
}

POST /api/transfers/wire-transfer/
{
  "recipient_name": "string",
  "bank_name": "string",
  "account_number": "string",
  "ifsc_code": "string",
  "amount": "number",
  "description": "string",
  "pin": "string"
}
Response: {
  "success": "boolean",
  "transaction_id": "string",
  "fee": "number"
}
```

#### **Chat System** (`/chat`)
**File:** `src/pages/Chat.jsx`

**Features:**
- Chat list sidebar (desktop) / full-screen (mobile)
- Real-time messaging interface
- Photo sharing capability
- Support agent chat
- User-to-user messaging
- Online status indicators
- Unread message counters

**API Calls Needed:**
```javascript
GET /api/chat/conversations/     # Get user's chat conversations
GET /api/chat/messages/{chat_id}/ # Get messages for specific chat
POST /api/chat/send-message/
{
  "chat_id": "number",
  "message": "string",
  "photo": "base64_string"  // optional
}
WebSocket: /ws/chat/{chat_id}/   # Real-time messaging
```

**Data Structures:**
```javascript
// Conversations
[{
  "id": "number",
  "user": "string",
  "avatar": "string",
  "last_message": "string",
  "time": "string",
  "unread": "number",
  "online": "boolean"
}]

// Messages
[{
  "id": "number",
  "text": "string",
  "photo": "url",  // optional
  "sender": "me|user|agent",
  "time": "string"
}]
```

#### **Settings** (`/settings`)
**File:** `src/pages/Settings.jsx`

**Features:**
- Change PIN (4-digit)
- Change password
- Transaction reporting
- Account logout
- Profile information display

**API Calls Needed:**
```javascript
PUT /api/user/change-pin/
{
  "current_pin": "string",
  "new_pin": "string"
}

PUT /api/user/change-password/
{
  "current_password": "string",
  "new_password": "string"
}

POST /api/reports/transaction/
{
  "transaction_id": "number",
  "reason": "string"
}

POST /api/auth/logout/
```

### 3. Admin Panel

#### **Admin Dashboard** (`/admin`)
**File:** `src/pages/Admin.jsx`

**Features:** (Currently placeholder)
- User management
- Transaction monitoring
- System reports
- Admin controls

**API Calls Needed:** (To be defined based on admin requirements)

## 🔐 Authentication & Security

### **JWT Token Management**
- Access tokens stored in localStorage
- Refresh token rotation
- Automatic token refresh on expiry
- Secure logout (token invalidation)

### **Route Protection**
- `PrivateRoute`: Protects authenticated pages
- `AdminRoute`: Protects admin-only pages
- Automatic redirects based on auth status

## 🎨 UI Components

### **Common Components**
- `PrivateRoute`: Route guard for authenticated users
- `AdminRoute`: Route guard for admin users

### **Icons & Styling**
- Feather icons for consistent UI
- Tailwind CSS for styling
- Custom animations and transitions
- Responsive design (mobile-first)

## 📊 Data Models

### **User Model**
```javascript
{
  "id": "number",
  "first_name": "string",
  "last_name": "string",
  "email": "string",
  "phone": "string",
  "country": "string",
  "residential_address": "string",
  "account_number": "string",  // 10 digits, format: ACC000XXXX
  "balance": "number",
  "is_verified": "boolean",
  "is_admin": "boolean",
  "transfer_pin": "string",    // 4 digits
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### **Transaction Model**
```javascript
{
  "id": "number",
  "sender_account": "string",
  "receiver_account": "string",
  "amount": "number",
  "type": "yeet_transfer|wire_transfer",
  "status": "pending|completed|failed",
  "description": "string",
  "fee": "number",
  "created_at": "datetime",
  "completed_at": "datetime"
}
```

### **Chat/Message Model**
```javascript
{
  "id": "number",
  "chat_id": "number",
  "sender_id": "number",
  "message": "string",
  "photo_url": "string",  // optional
  "message_type": "text|photo",
  "created_at": "datetime",
  "read_at": "datetime"   // optional
}
```

## 🔧 Backend API Requirements

### **Authentication Endpoints**
1. `POST /api/auth/login/` - User login
2. `POST /api/auth/register/` - User registration
3. `POST /api/auth/logout/` - User logout
4. `POST /api/auth/refresh/` - Token refresh
5. `GET /api/auth/me/` - Get current user

### **User Management**
1. `GET /api/user/profile/` - Get user profile
2. `PUT /api/user/profile/` - Update user profile
3. `PUT /api/user/change-pin/` - Change transfer PIN
4. `PUT /api/user/change-password/` - Change password

### **Transfer Operations**
1. `POST /api/transfers/validate-receiver/` - Validate receiver account
2. `POST /api/transfers/yeet-transfer/` - Internal transfer
3. `POST /api/transfers/wire-transfer/` - External transfer
4. `GET /api/transfers/history/` - Transfer history

### **Chat System**
1. `GET /api/chat/conversations/` - Get user conversations
2. `GET /api/chat/messages/{chat_id}/` - Get chat messages
3. `POST /api/chat/send-message/` - Send message
4. `WebSocket /ws/chat/{chat_id}/` - Real-time messaging

### **Notifications**
1. `GET /api/notifications/` - Get notifications
2. `PUT /api/notifications/{id}/read/` - Mark as read

### **Reports**
1. `POST /api/reports/transaction/` - Report transaction issue

### **Admin Endpoints** (Future)
1. `GET /api/admin/users/` - User management
2. `GET /api/admin/transactions/` - Transaction monitoring
3. `GET /api/admin/reports/` - System reports

## 🗄️ Database Schema Requirements

### **Core Tables**
- `users` - User accounts and profiles
- `transactions` - Transfer records
- `chats` - Chat conversations
- `messages` - Individual messages
- `notifications` - User notifications
- `reports` - Transaction reports

### **Relationships**
- Users can send/receive transactions
- Users can participate in multiple chats
- Chats contain multiple messages
- Users receive notifications
- Users can report transactions

## 🔒 Security Considerations

1. **Password Hashing**: Secure password storage
2. **JWT Security**: Proper token validation and expiration
3. **Rate Limiting**: API rate limiting for sensitive operations
4. **Input Validation**: Comprehensive input sanitization
5. **PIN Security**: Secure PIN storage and validation
6. **File Upload Security**: Safe photo upload handling

## 📱 Mobile Responsiveness

All pages are designed mobile-first with:
- Responsive layouts
- Touch-friendly interactions
- Optimized chat interface for mobile
- Proper viewport handling

## 🎯 Demo Data

**Default Login Credentials:**
- Email/Phone/Account: Any from demo users
- Password: `demo123`

**Demo Users:**
1. John Doe (Premium) - john@demo.com
2. Jane Smith (Basic) - jane@demo.com
3. Admin User (Business) - admin@demo.com

This documentation provides a complete blueprint for building the Yeet Bank backend API that supports all frontend functionality.</content>
<parameter name="filePath">c:\Users\hp\Desktop\yeet bank\FRONTEND_README.md