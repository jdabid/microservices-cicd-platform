import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import axios from 'axios'
import { useAuth } from '../context/AuthContext'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function DashboardPage() {
  const { user, logout } = useAuth()
  const [apiHealth, setApiHealth] = useState(null)

  useEffect(() => {
    checkApiHealth()
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

  return (
    <div className="dashboard">
      <header className="App-header">
        <div className="header-content">
          <h1>Medical Appointments System</h1>
          <div className="header-actions">
            <span className="user-greeting">Welcome, {user?.full_name}</span>
            <button className="btn-logout" onClick={logout}>
              Sign Out
            </button>
          </div>
        </div>
        <div className="api-status">
          API Status:
          <span className={`status-badge ${apiHealth?.status === 'healthy' ? 'healthy' : 'unhealthy'}`}>
            {apiHealth?.status || 'checking...'}
          </span>
        </div>
      </header>

      <main className="App-main">
        <section className="dashboard-welcome">
          <h2>Dashboard</h2>
          <div className="user-info-card">
            <h3>Your Profile</h3>
            <div className="user-details">
              <p><strong>Name:</strong> {user?.full_name}</p>
              <p><strong>Email:</strong> {user?.email}</p>
              <p><strong>Status:</strong> <span className="status-badge healthy">{user?.is_active ? 'Active' : 'Inactive'}</span></p>
              <p><strong>Member since:</strong> {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}</p>
            </div>
          </div>
        </section>

        <section className="dashboard-nav">
          <h2>Quick Access</h2>
          <div className="nav-cards">
            <Link to="/appointments" className="nav-card">
              <div className="nav-card-icon">&#x1F4C5;</div>
              <h3>Appointments</h3>
              <p>Create and manage appointments</p>
            </Link>
            <div className="nav-card nav-card-disabled">
              <div className="nav-card-icon">&#x1F465;</div>
              <h3>Patients</h3>
              <p>Coming soon</p>
            </div>
          </div>
        </section>
      </main>

      <footer className="App-footer">
        <p>Microservices CI/CD Platform - Portfolio Project</p>
        <p>Architecture: Vertical Slice + CQRS | Stack: FastAPI + React + Docker</p>
      </footer>
    </div>
  )
}

export default DashboardPage
