import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card'
import { Button } from '../components/ui/Button'

export default function Login() {
    const { setAuth, isAuthenticated } = useAuthStore()
    const navigate = useNavigate()

    useEffect(() => {
        if (isAuthenticated) {
            navigate('/')
            return
        }

        // Handle OAuth callback - check for token in URL
        const urlParams = new URLSearchParams(window.location.search)
        const token = urlParams.get('token')
        const userId = urlParams.get('user_id')

        if (token && userId) {
            // Fetch user profile with the token
            fetch('http://localhost:8080/api/auth/profile', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })
                .then(res => res.json())
                .then(userData => {
                    setAuth(userData, token)
                    // Clean up URL
                    window.history.replaceState({}, document.title, '/login')
                    navigate('/')
                })
                .catch(err => {
                    console.error('Failed to fetch user profile:', err)
                })
        }
    }, [isAuthenticated, navigate, setAuth])

    const handleLogin = () => {
        // Redirect to backend OAuth endpoint
        window.location.href = 'http://localhost:8080/api/auth/login'
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-background p-4">
            <div className="absolute inset-0 overflow-hidden">
                <div className="absolute -top-[40%] -left-[20%] w-[70%] h-[70%] rounded-full bg-primary/20 blur-[100px]" />
                <div className="absolute -bottom-[40%] -right-[20%] w-[70%] h-[70%] rounded-full bg-secondary/20 blur-[100px]" />
            </div>

            <Card className="w-full max-w-md relative z-10 border-white/10 bg-surface/50 backdrop-blur-xl shadow-2xl">
                <CardHeader className="text-center pb-2">
                    <div className="mx-auto w-16 h-16 bg-gradient-to-br from-primary to-secondary rounded-xl flex items-center justify-center mb-4 shadow-lg shadow-primary/20">
                        <span className="text-3xl">🎓</span>
                    </div>
                    <CardTitle className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-white/60">
                        Academic Assistant
                    </CardTitle>
                    <p className="text-text/60 mt-2">
                        Your personal command center for Google Classroom
                    </p>
                </CardHeader>
                <CardContent className="space-y-6 pt-6">
                    <div className="space-y-4">
                        <div className="p-4 rounded-lg bg-primary/10 border border-primary/20">
                            <h3 className="font-semibold text-primary mb-1 flex items-center gap-2">
                                <span>🚀</span> Modern & Fast
                            </h3>
                            <p className="text-sm text-text/70">
                                Rebuilt from the ground up for speed and reliability.
                            </p>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div className="p-3 rounded-lg bg-white/5 border border-white/10 text-center">
                                <span className="text-2xl mb-2 block">📅</span>
                                <p className="text-xs font-medium text-text/60">Smart Calendar</p>
                            </div>
                            <div className="p-3 rounded-lg bg-white/5 border border-white/10 text-center">
                                <span className="text-2xl mb-2 block">📱</span>
                                <p className="text-xs font-medium text-text/60">WhatsApp Alerts</p>
                            </div>
                        </div>
                    </div>

                    <Button
                        onClick={handleLogin}
                        className="w-full h-12 text-lg font-medium shadow-lg shadow-primary/20 hover:shadow-primary/40 transition-all"
                    >
                        <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                            <path
                                fill="currentColor"
                                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                            />
                            <path
                                fill="currentColor"
                                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                            />
                            <path
                                fill="currentColor"
                                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                            />
                            <path
                                fill="currentColor"
                                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                            />
                        </svg>
                        Sign in with Google
                    </Button>
                </CardContent>
            </Card>
        </div>
    )
}
