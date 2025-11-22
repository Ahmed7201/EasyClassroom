# Academic Assistant - Quick Start Guide

## 🚀 Running the Application

### Backend (Go)
```bash
cd backend
go run cmd/server/main.go
```
The backend will start on `http://localhost:8080`

### Frontend (React)
```bash
cd frontend
npm install  # First time only
npm run dev
```
The frontend will start on `http://localhost:5173`

## 📋 Features Implemented

### ✅ Core Features
- **Google Classroom Integration** - Fetch courses and assignments
- **Google Calendar Integration** - View and create events
- **Assignment Categorization** - Auto-detect assignment types (Quiz, Exam, Lab, etc.)
- **Grade Calculator** - Weighted grade calculation with category breakdown
- **Calendar Sync** - Sync assignments to Google Calendar with reminders
- **WhatsApp Notifications** - Daily summaries and new assignment alerts
- **Timezone Handling** - User-specific timezone support with external validation
- **Gmail Integration** - Send emails via Gmail API
- **System Integration** - Open files with default applications

### 🎨 Frontend Pages
- **Login** - Google OAuth authentication
- **Dashboard** - Course overview with cards
- **Course Details** - Assignments, materials, grades, and people tabs
- **Calendar** - Monthly view with assignment events
- **Settings** - User preferences and timezone configuration

### 🔧 API Endpoints

#### Authentication
- `POST /api/auth/login` - Initiate Google OAuth
- `GET /api/auth/callback` - OAuth callback
- `POST /api/auth/refresh` - Refresh JWT token
- `POST /api/auth/logout` - Logout
- `GET /api/auth/profile` - Get user profile

#### Courses
- `GET /api/courses` - List all courses
- `GET /api/courses/:id` - Get course details
- `GET /api/courses/:id/assignments` - Get course assignments
- `GET /api/courses/:id/grades` - Get grade breakdown

#### Calendar
- `GET /api/calendar/events` - List upcoming events
- `POST /api/calendar/events` - Create event
- `DELETE /api/calendar/events/:id` - Delete event
- `POST /api/calendar/sync` - Sync assignments to calendar

#### WhatsApp
- `POST /api/whatsapp/configure` - Save WhatsApp settings
- `POST /api/whatsapp/test` - Send test message
- `POST /api/whatsapp/send-summary` - Send daily summary
- `GET /api/whatsapp/settings` - Get WhatsApp settings

#### Settings
- `GET /api/settings` - Get user settings
- `PUT /api/settings` - Update user settings
- `GET /api/settings/verify-timezone` - Verify timezone with external API

#### Gmail
- `POST /api/gmail/send` - Send email

#### System
- `POST /api/system/open` - Open file with default application

## 🔐 Environment Setup

### Backend (.env)
```env
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URL=http://localhost:8080/api/auth/callback
JWT_SECRET=your_jwt_secret
DATABASE_PATH=./data/academic_assistant.db
FRONTEND_URL=http://localhost:5173
PORT=8080
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8080/api
```

## 📦 Dependencies

### Backend
- Gin (Web framework)
- GORM (ORM)
- Google API clients (Classroom, Calendar, Gmail)
- JWT-go (Authentication)
- godotenv (Environment variables)

### Frontend
- React 18
- TypeScript
- Vite 4
- TanStack Query (Data fetching)
- Zustand (State management)
- Axios (HTTP client)
- React Router (Routing)
- Tailwind CSS (Styling)
- Radix UI (Components)
- date-fns (Date utilities)
- Lucide React (Icons)

## 🎯 Next Steps (Optional)
- [ ] Search functionality across assignments
- [ ] Unit tests for backend
- [ ] Integration tests for APIs
- [ ] Frontend component tests
- [ ] Performance optimization
- [ ] Accessibility audit
- [ ] Cross-browser testing

## 📝 Notes
- The backend uses SQLite for data storage
- OAuth tokens are stored in the database
- JWT tokens expire after 24 hours
- WhatsApp notifications use CallMeBot API
- Calendar events are created 6 hours before assignment deadlines
