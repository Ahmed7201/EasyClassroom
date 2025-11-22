# Academic Assistant - React Migration

## Project Structure

This is the migrated version of the Academic Assistant application, rebuilt with modern technologies:

- **Backend**: Go (Golang) with Gin framework
- **Frontend**: React 18 + Vite + TypeScript
- **State**: Zustand + TanStack Query
- **Styling**: Tailwind CSS

## Getting Started

### Prerequisites

- Go 1.21+
- Node.js 18+
- Google Cloud Console project with OAuth credentials

### Backend Setup

```bash
cd backend

# Install dependencies
go mod download

# Copy environment template
cp .env.example .env

# Edit .env with your Google OAuth credentials
# Get credentials from: https://console.cloud.google.com/apis/credentials

# Run the server
go run cmd/server/main.go
```

Backend will start on `http://localhost:8080`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will start on `http://localhost:5173`

## Architecture

### Backend (Go)

- `cmd/server/main.go` - Entry point with routing
- `internal/api/` - HTTP handlers
- `internal/services/` - Business logic
- `internal/models/` - Data models
- `internal/db/` - Database layer

### Frontend (React)

- `src/pages/` - Route pages
- `src/components/` - Reusable components
- `src/api/` - API client layer
- `src/store/` - Global state (Zustand)
- `src/hooks/` - Custom hooks

## Development Roadmap

- [x] Project scaffolding
- [ ] OAuth authentication
- [ ] Google Classroom API integration
- [ ] Calendar integration
- [ ] WhatsApp notifications
- [ ] Course dashboard
- [ ] Grading engine
- [ ] File downloads
- [ ] I18n/Accessibility

## License

MIT
