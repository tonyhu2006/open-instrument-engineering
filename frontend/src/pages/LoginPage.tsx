import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Loader2, AlertCircle } from 'lucide-react'
import { authApi } from '@/lib/api'

export function LoginPage() {
  const navigate = useNavigate()
  
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setIsLoading(true)
    
    try {
      const response = await authApi.login({ username, password })
      localStorage.setItem('access_token', response.access)
      localStorage.setItem('refresh_token', response.refresh)
      navigate('/')
    } catch (err: unknown) {
      const errorObj = err as { response?: { data?: { detail?: string } } }
      setError(errorObj.response?.data?.detail || 'Login failed. Please check your credentials.')
    } finally {
      setIsLoading(false)
    }
  }
  
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <div className="w-full max-w-md p-8">
        <div className="bg-white/10 backdrop-blur-lg rounded-2xl shadow-2xl p-8 border border-white/20">
          {/* Logo and Title */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-blue-500/20 mb-4">
              <svg
                className="w-8 h-8 text-blue-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"
                />
              </svg>
            </div>
            <h1 className="text-2xl font-bold text-white">OpenInstrument</h1>
            <p className="text-slate-400 mt-2">AI-Driven Instrumentation Design Platform</p>
          </div>
          
          {/* Error Message */}
          {error && (
            <div className="mb-6 p-4 rounded-lg bg-red-500/20 border border-red-500/50 flex items-center gap-3">
              <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
              <p className="text-red-300 text-sm">{error}</p>
            </div>
          )}
          
          {/* Login Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-slate-300 mb-2">
                Username
              </label>
              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                placeholder="Enter your username"
                required
                autoComplete="username"
              />
            </div>
            
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-slate-300 mb-2">
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                placeholder="Enter your password"
                required
                autoComplete="current-password"
              />
            </div>
            
            <Button
              type="submit"
              disabled={isLoading}
              className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Signing in...
                </>
              ) : (
                'Sign In'
              )}
            </Button>
          </form>
          
          {/* Demo Accounts */}
          <div className="mt-8 pt-6 border-t border-white/10">
            <p className="text-center text-slate-400 text-sm mb-4">Demo Accounts</p>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="p-2 rounded bg-white/5 text-slate-300">
                <span className="font-medium">admin</span> / admin123
              </div>
              <div className="p-2 rounded bg-white/5 text-slate-300">
                <span className="font-medium">proj_engineer</span> / demo123
              </div>
              <div className="p-2 rounded bg-white/5 text-slate-300">
                <span className="font-medium">inst_engineer</span> / demo123
              </div>
              <div className="p-2 rounded bg-white/5 text-slate-300">
                <span className="font-medium">proc_engineer</span> / demo123
              </div>
            </div>
          </div>
        </div>
        
        {/* Footer */}
        <p className="text-center text-slate-500 text-sm mt-6">
          © 2025 OpenInstrument. Open Source under AGPL-3.0
        </p>
      </div>
    </div>
  )
}
