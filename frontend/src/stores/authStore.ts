import { create } from 'zustand'
import { authApi, type UserProfile } from '@/lib/api'

interface AuthState {
  user: UserProfile | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  
  login: (username: string, password: string) => Promise<boolean>
  logout: () => void
  fetchUser: () => Promise<void>
  checkAuth: () => void
  clearError: () => void
}

export const useAuthStore = create<AuthState>()((set, get) => ({
  user: null,
  isAuthenticated: !!localStorage.getItem('access_token'),
  isLoading: false,
  error: null,
  
  login: async (username: string, password: string) => {
    set({ isLoading: true, error: null })
    try {
      const response = await authApi.login({ username, password })
      
      // Store tokens
      localStorage.setItem('access_token', response.access)
      localStorage.setItem('refresh_token', response.refresh)
      
      set({
        isAuthenticated: true,
        isLoading: false,
      })
      
      // Fetch user profile
      await get().fetchUser()
      
      return true
    } catch (error: unknown) {
      const errorObj = error as { response?: { data?: { detail?: string } } }
      const message = errorObj.response?.data?.detail || 'Login failed. Please check your credentials.'
      set({
        isLoading: false,
        error: message,
        isAuthenticated: false,
      })
      return false
    }
  },
  
  logout: () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    set({
      user: null,
      isAuthenticated: false,
      error: null,
    })
  },
  
  fetchUser: async () => {
    try {
      const user = await authApi.me()
      set({ user })
    } catch {
      // If fetching user fails, logout
      get().logout()
    }
  },
  
  checkAuth: () => {
    const token = localStorage.getItem('access_token')
    set({ isAuthenticated: !!token })
  },
  
  clearError: () => set({ error: null }),
}))
