import React, { createContext, useContext, useState, useEffect } from 'react'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(localStorage.getItem('token'))
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (token) {
      validateToken()
    } else {
      setLoading(false)
    }
  }, [])

  const validateToken = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/v1/auth/me`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setUser(response.data)
    } catch (err) {
      console.error('Token validation failed:', err)
      localStorage.removeItem('token')
      setToken(null)
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  const login = async (email, password) => {
    const response = await axios.post(`${API_URL}/api/v1/auth/login`, {
      email,
      password
    })
    const { access_token } = response.data
    localStorage.setItem('token', access_token)
    setToken(access_token)

    const meResponse = await axios.get(`${API_URL}/api/v1/auth/me`, {
      headers: { Authorization: `Bearer ${access_token}` }
    })
    setUser(meResponse.data)
    return response.data
  }

  const register = async (email, password, full_name) => {
    const response = await axios.post(`${API_URL}/api/v1/auth/register`, {
      email,
      password,
      full_name
    })
    const { access_token } = response.data
    localStorage.setItem('token', access_token)
    setToken(access_token)

    const meResponse = await axios.get(`${API_URL}/api/v1/auth/me`, {
      headers: { Authorization: `Bearer ${access_token}` }
    })
    setUser(meResponse.data)
    return response.data
  }

  const logout = () => {
    localStorage.removeItem('token')
    setToken(null)
    setUser(null)
  }

  const value = {
    user,
    token,
    loading,
    login,
    register,
    logout,
    isAuthenticated: !!user && !!token
  }

  return (
    <AuthContext.Provider value={value}>
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

export default AuthContext
