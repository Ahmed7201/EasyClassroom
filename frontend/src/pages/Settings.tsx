import { useEffect, useState } from 'react'
import { Save, Bell, MessageSquare, Clock } from 'lucide-react'
import { Card, CardContent } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { whatsappApi } from '../api/whatsapp'
import { WhatsAppSettings } from '../types/models'
import { useAuthStore } from '../store/authStore'

export default function Settings() {
    const { logout } = useAuthStore()
    const [settings, setSettings] = useState<WhatsAppSettings>({
        phoneNumber: '',
        apiKey: '',
        dailySummaryEnabled: false,
        newAssignmentAlerts: false,
        summaryTime: '08:00'
    })
    const [isLoading, setIsLoading] = useState(true)
    const [isSaving, setIsSaving] = useState(false)
    const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null)

    useEffect(() => {
        const fetchSettings = async () => {
            try {
                const data = await whatsappApi.getSettings()
                setSettings(data)
            } catch (error) {
                console.error('Failed to fetch settings:', error)
            } finally {
                setIsLoading(false)
            }
        }

        fetchSettings()
    }, [])

    const handleSave = async () => {
        setIsSaving(true)
        setMessage(null)
        try {
            await whatsappApi.updateSettings(settings)
            setMessage({ type: 'success', text: 'Settings saved successfully!' })
        } catch (error) {
            setMessage({ type: 'error', text: 'Failed to save settings.' })
        } finally {
            setIsSaving(false)
        }
    }

    const handleTest = async () => {
        try {
            await whatsappApi.sendTest()
            setMessage({ type: 'success', text: 'Test message sent! Check your WhatsApp.' })
        } catch (error) {
            setMessage({ type: 'error', text: 'Failed to send test message.' })
        }
    }

    if (isLoading) {
        return <div className="p-8 text-center">Loading settings...</div>
    }

    return (
        <div className="container mx-auto px-4 py-8 max-w-2xl">
            <h1 className="text-3xl font-bold mb-8">Settings</h1>

            <Card className="bg-surface/30 border-white/10 mb-8">
                <CardContent className="p-6">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="p-2 bg-green-500/20 rounded-lg text-green-400">
                            <MessageSquare className="w-6 h-6" />
                        </div>
                        <div>
                            <h2 className="text-xl font-bold">WhatsApp Notifications</h2>
                            <p className="text-sm text-text/60">Configure how you want to receive updates</p>
                        </div>
                    </div>

                    <div className="space-y-6">
                        <div>
                            <label className="block text-sm font-medium mb-2">Phone Number</label>
                            <input
                                type="text"
                                placeholder="+1234567890"
                                value={settings.phoneNumber}
                                onChange={(e) => setSettings({ ...settings, phoneNumber: e.target.value })}
                                className="w-full px-4 py-2 bg-black/20 border border-white/10 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
                            />
                            <p className="text-xs text-text/40 mt-1">Include country code (e.g., +1 for US)</p>
                        </div>

                        <div>
                            <label className="block text-sm font-medium mb-2">API Key</label>
                            <input
                                type="password"
                                placeholder="Your WhatsApp API Key"
                                value={settings.apiKey}
                                onChange={(e) => setSettings({ ...settings, apiKey: e.target.value })}
                                className="w-full px-4 py-2 bg-black/20 border border-white/10 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
                            />
                        </div>

                        <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                            <div className="flex items-center gap-3">
                                <Bell className="w-5 h-5 text-primary" />
                                <div>
                                    <div className="font-medium">New Assignment Alerts</div>
                                    <div className="text-xs text-text/60">Get notified when new work is posted</div>
                                </div>
                            </div>
                            <input
                                type="checkbox"
                                checked={settings.newAssignmentAlerts}
                                onChange={(e) => setSettings({ ...settings, newAssignmentAlerts: e.target.checked })}
                                className="w-5 h-5 rounded border-white/10 bg-black/20 text-primary focus:ring-primary"
                            />
                        </div>

                        <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                            <div className="flex items-center gap-3">
                                <Clock className="w-5 h-5 text-secondary" />
                                <div>
                                    <div className="font-medium">Daily Summary</div>
                                    <div className="text-xs text-text/60">Receive a daily digest of upcoming deadlines</div>
                                </div>
                            </div>
                            <div className="flex items-center gap-4">
                                <input
                                    type="time"
                                    value={settings.summaryTime}
                                    onChange={(e) => setSettings({ ...settings, summaryTime: e.target.value })}
                                    className="px-2 py-1 bg-black/20 border border-white/10 rounded focus:outline-none focus:ring-1 focus:ring-secondary"
                                    disabled={!settings.dailySummaryEnabled}
                                />
                                <input
                                    type="checkbox"
                                    checked={settings.dailySummaryEnabled}
                                    onChange={(e) => setSettings({ ...settings, dailySummaryEnabled: e.target.checked })}
                                    className="w-5 h-5 rounded border-white/10 bg-black/20 text-secondary focus:ring-secondary"
                                />
                            </div>
                        </div>

                        {message && (
                            <div className={`p-3 rounded-lg text-sm ${message.type === 'success' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                                {message.text}
                            </div>
                        )}

                        <div className="flex gap-4 pt-4">
                            <Button onClick={handleSave} disabled={isSaving} className="flex-1">
                                <Save className="w-4 h-4 mr-2" />
                                {isSaving ? 'Saving...' : 'Save Settings'}
                            </Button>
                            <Button variant="outline" onClick={handleTest}>
                                Test Connection
                            </Button>
                        </div>
                    </div>
                </CardContent>
            </Card>

            <Card className="bg-surface/30 border-white/10">
                <CardContent className="p-6">
                    <h2 className="text-xl font-bold mb-4">Account</h2>
                    <Button variant="danger" className="w-full" onClick={logout}>
                        Sign Out
                    </Button>
                </CardContent>
            </Card>
        </div>
    )
}
