import { createContext, useContext, useState, useEffect, type ReactNode } from 'react'
import { authApi, type UserProfile } from '@/lib/api'

interface AuthContextType {
  user: UserProfile | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  login: (username: string, password: string) => Promise<boolean>
  logout: () => void
  clearError: () => void
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(null)
  const [isAuthenticated, setIsAuthenticated] = useState(() => !!localStorage.getItem('access_token'))
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // Check if we have a token and try to fetch user
    const token = localStorage.getItem('access_token')
    if (token && !user) {
      fetchUser()
    }
  }, [])

  const fetchUser = async () => {
    try {
      const userData = await authApi.me()
      setUser(userData)
    } catch {
      // Token is invalid, logout
      logout()
    }
  }

  const login = async (username: string, password: string): Promise<boolean> => {
    setIsLoading(true)
    setError(null)
    
    try {
      const response = await authApi.login({ username, password })
      
      localStorage.setItem('access_token', response.access)
      localStorage.setItem('refresh_token', response.refresh)
      
      setIsAuthenticated(true)
      setIsLoading(false)
      
      await fetchUser()
      
      return true
    } catch (err: unknown) {
      const errorObj = err as { response?: { data?: { detail?: string } } }
      const message = errorObj.response?.data?.detail || 'Login failed. Please check your credentials.'
      setError(message)
      setIsLoading(false)
      setIsAuthenticated(false)
      return false
    }
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setUser(null)
    setIsAuthenticated(false)
    setError(null)
  }

  const clearError = () => setError(null)

  return (
    <AuthContext.Provider value={{
      user,
      isAuthenticated,
      isLoading,
      error,
      login,
      logout,
      clearError,
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
