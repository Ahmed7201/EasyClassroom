import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import Navbar from './components/layout/Navbar'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Course from './pages/Course'
import Assignments from './pages/Assignments'
import Calendar from './pages/Calendar'
import Settings from './pages/Settings'
import Grades from './pages/Grades'

function App() {
    const { isAuthenticated } = useAuthStore()

    return (
        <Router>
            <div className="min-h-screen bg-background text-text font-sans">
                {isAuthenticated && <Navbar />}
                <Routes>
                    <Route
                        path="/login"
                        element={!isAuthenticated ? <Login /> : <Navigate to="/" />}
                    />
                    <Route
                        path="/"
                        element={isAuthenticated ? <Dashboard /> : <Navigate to="/login" />}
                    />
                    <Route
                        path="/assignments"
                        element={isAuthenticated ? <Assignments /> : <Navigate to="/login" />}
                    />
                    <Route
                        path="/course/:id"
                        element={isAuthenticated ? <Course /> : <Navigate to="/login" />}
                    />
                    <Route
                        path="/calendar"
                        element={isAuthenticated ? <Calendar /> : <Navigate to="/login" />}
                    />
                    <Route
                        path="/grades"
                        element={isAuthenticated ? <Grades /> : <Navigate to="/login" />}
                    />
                    <Route
                        path="/settings"
                        element={isAuthenticated ? <Settings /> : <Navigate to="/login" />}
                    />
                </Routes>
            </div>
        </Router>
    )
}

export default App
