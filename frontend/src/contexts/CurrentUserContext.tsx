import { createContext, useContext, useEffect, useState, useCallback, type ReactNode } from 'react'
import { authApi, type UserProfile } from '@/lib/api'

interface CurrentUserContextValue {
  user: UserProfile | null
  loading: boolean
  error: string | null
  refresh: () => Promise<void>
}

const CurrentUserContext = createContext<CurrentUserContextValue | undefined>(undefined)

export function CurrentUserProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      setUser(null)
      setLoading(false)
      return
    }
    setLoading(true)
    setError(null)
    try {
      const me = await authApi.me()
      setUser(me)
    } catch (e: unknown) {
      const err = e as { response?: { status?: number } }
      if (err.response?.status === 401) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
      }
      setError('Failed to load user profile')
      setUser(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    refresh()
  }, [refresh])

  return (
    <CurrentUserContext.Provider value={{ user, loading, error, refresh }}>
      {children}
    </CurrentUserContext.Provider>
  )
}

export function useCurrentUser(): CurrentUserContextValue {
  const ctx = useContext(CurrentUserContext)
  if (!ctx) {
    throw new Error('useCurrentUser must be used within CurrentUserProvider')
  }
  return ctx
}
