import React, { useState, useEffect } from 'react'
import axios from 'axios'
import AppointmentList from './components/AppointmentList'
import AppointmentForm from './components/AppointmentForm'
import './App.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [appointments, setAppointments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [apiHealth, setApiHealth] = useState(null)

  useEffect(() => {
    checkApiHealth()
    fetchAppointments()
  }, [])

  const checkApiHealth = async () => {
    try {
      const response = await axios.get(`${API_URL}/health`)
      setApiHealth(response.data)
    } catch (err) {
      console.error('API Health check failed:', err)
      setApiHealth({ status: 'unhealthy' })
    }
  }

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
        <h1>🏥 Medical Appointments System</h1>
        <div className="api-status">
          API Status:
          <span className={`status-badge ${apiHealth?.status === 'healthy' ? 'healthy' : 'unhealthy'}`}>
            {apiHealth?.status || 'checking...'}
          </span>
        </div>
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

export default App