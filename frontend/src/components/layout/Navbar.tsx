import { Link, useLocation } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'
import { Button } from '../ui/Button'

export default function Navbar() {
    const { user, logout } = useAuthStore()
    const location = useLocation()

    const isActive = (path: string) => location.pathname === path

    return (
        <nav className="sticky top-0 z-50 w-full border-b border-white/10 bg-background/80 backdrop-blur-xl">
            <div className="container mx-auto px-4 h-16 flex items-center justify-between">
                <div className="flex items-center gap-8">
                    <Link to="/" className="flex items-center gap-2 font-bold text-xl text-primary">
                        <span className="text-2xl">📚</span>
                        <span>Academic Assistant</span>
                    </Link>

                    <div className="hidden md:flex items-center gap-1">
                        <Link to="/">
                            <Button variant={isActive('/') ? 'secondary' : 'ghost'} size="sm">
                                Dashboard
                            </Button>
                        </Link>
                        <Link to="/assignments">
                            <Button variant={isActive('/assignments') ? 'secondary' : 'ghost'} size="sm">
                                Assignments
                            </Button>
                        </Link>
                        <Link to="/calendar">
                            <Button variant={isActive('/calendar') ? 'secondary' : 'ghost'} size="sm">
                                Calendar
                            </Button>
                        </Link>
                        <Link to="/grades">
                            <Button variant={isActive('/grades') ? 'secondary' : 'ghost'} size="sm">
                                Grades
                            </Button>
                        </Link>
                    </div>
                </div>

                <div className="flex items-center gap-4">
                    {user && (
                        <div className="flex items-center gap-3">
                            <div className="hidden md:block text-right">
                                <p className="text-sm font-medium leading-none">{user.name}</p>
                                <p className="text-xs text-text/60">{user.email}</p>
                            </div>
                            {user.picture ? (
                                <img
                                    src={user.picture}
                                    alt={user.name}
                                    className="h-9 w-9 rounded-full border border-white/10"
                                />
                            ) : (
                                <div className="h-9 w-9 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold">
                                    {user.name[0]}
                                </div>
                            )}

                            <Link to="/settings">
                                <Button variant="ghost" size="icon" title="Settings">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                        <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.1a2 2 0 0 1-1-1.72v-.51a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"></path>
                                        <circle cx="12" cy="12" r="3"></circle>
                                    </svg>
                                </Button>
                            </Link>
                            <Button variant="ghost" size="icon" onClick={logout} title="Logout">
                                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                                    <polyline points="16 17 21 12 16 7"></polyline>
                                    <line x1="21" y1="12" x2="9" y2="12"></line>
                                </svg>
                            </Button>
                        </div>
                    )}
                </div>
            </div>
        </nav>
    )
}
