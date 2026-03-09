import React, { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import axios from 'axios'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import AppointmentList from './components/AppointmentList'
import AppointmentForm from './components/AppointmentForm'
import './App.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function AppointmentsPage() {
  const [appointments, setAppointments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchAppointments()
  }, [])

  const fetchAppointments = async () => {
    try {
      setLoading(true)
      const response = await axios.get(`${API_URL}/api/v1/appointments/`)
      setAppointments(response.data.items || [])
      setError(null)
    } catch (err) {
      console.error('Error fetching appointments:', err)
      setError('Failed to fetch appointments. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleAppointmentCreated = () => {
    fetchAppointments()
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>Medical Appointments System</h1>
      </header>

      <main className="App-main">
        <section className="create-section">
          <h2>Create New Appointment</h2>
          <AppointmentForm
            apiUrl={API_URL}
            onAppointmentCreated={handleAppointmentCreated}
          />
        </section>

        <section className="list-section">
          <h2>Appointments List</h2>
          {loading && <p className="loading">Loading appointments...</p>}
          {error && <p className="error">{error}</p>}
          {!loading && !error && (
            <AppointmentList
              appointments={appointments}
              onRefresh={fetchAppointments}
            />
          )}
        </section>
      </main>

      <footer className="App-footer">
        <p>Microservices CI/CD Platform - Portfolio Project</p>
        <p>Architecture: Vertical Slice + CQRS | Stack: FastAPI + React + Docker</p>
      </footer>
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/appointments"
            element={
              <ProtectedRoute>
                <AppointmentsPage />
              </ProtectedRoute>
            }
          />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App
