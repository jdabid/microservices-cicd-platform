import React, { useState, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import axios from 'axios'
import { useAuth } from '../context/AuthContext'
import AppointmentFilters from '../components/AppointmentFilters'
import AppointmentForm from '../components/AppointmentForm'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const STATUS_COLORS = {
  scheduled: '#3b82f6',
  confirmed: '#22c55e',
  cancelled: '#ef4444',
  completed: '#6b7280',
  no_show: '#f97316'
}

const STATUS_LABELS = {
  scheduled: 'Scheduled',
  confirmed: 'Confirmed',
  cancelled: 'Cancelled',
  completed: 'Completed',
  no_show: 'No Show'
}

function AppointmentsPage() {
  const { user, token, logout } = useAuth()
  const [appointments, setAppointments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [total, setTotal] = useState(0)
  const [filters, setFilters] = useState({})
  const [showForm, setShowForm] = useState(false)
  const [editingAppointment, setEditingAppointment] = useState(null)

  const authHeaders = { Authorization: `Bearer ${token}` }

  const fetchAppointments = useCallback(async (currentPage, currentFilters) => {
    try {
      setLoading(true)
      const params = { page: currentPage, page_size: 20, ...currentFilters }
      const response = await axios.get(`${API_URL}/api/v1/appointments/`, {
        headers: authHeaders,
        params
      })
      setAppointments(response.data.items || [])
      setTotalPages(response.data.total_pages || 1)
      setTotal(response.data.total || 0)
      setError(null)
    } catch (err) {
      console.error('Error fetching appointments:', err)
      if (err.response?.status === 401) {
        setError('Session expired. Please login again.')
      } else {
        setError('Failed to fetch appointments. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }, [token])

  useEffect(() => {
    fetchAppointments(page, filters)
  }, [page, filters, fetchAppointments])

  const handleApplyFilters = (newFilters) => {
    setPage(1)
    setFilters(newFilters)
  }

  const handleClearFilters = () => {
    setPage(1)
    setFilters({})
  }

  const handleAppointmentCreated = () => {
    setShowForm(false)
    setEditingAppointment(null)
    fetchAppointments(page, filters)
  }

  const handleEdit = (appointment) => {
    setEditingAppointment(appointment)
    setShowForm(true)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const handleCancel = async (appointmentId) => {
    if (!window.confirm('Are you sure you want to cancel this appointment?')) return

    try {
      await axios.delete(`${API_URL}/api/v1/appointments/${appointmentId}`, {
        headers: authHeaders
      })
      fetchAppointments(page, filters)
    } catch (err) {
      console.error('Error cancelling appointment:', err)
      alert(err.response?.data?.detail || 'Failed to cancel appointment')
    }
  }

  const handleCloseForm = () => {
    setShowForm(false)
    setEditingAppointment(null)
  }

  const formatDateTime = (dateStr) => {
    if (!dateStr) return 'N/A'
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="dashboard">
      <header className="App-header">
        <div className="header-content">
          <h1>Medical Appointments System</h1>
          <div className="header-actions">
            <Link to="/dashboard" className="btn-back">Dashboard</Link>
            <span className="user-greeting">Welcome, {user?.full_name}</span>
            <button className="btn-logout" onClick={logout}>Sign Out</button>
          </div>
        </div>
      </header>

      <main className="App-main">
        {/* Form overlay */}
        {showForm && (
          <div className="form-overlay">
            <div className="form-modal">
              <div className="form-modal-header">
                <h2>{editingAppointment ? 'Edit Appointment' : 'New Appointment'}</h2>
                <button className="btn-close-modal" onClick={handleCloseForm}>&times;</button>
              </div>
              <AppointmentForm
                apiUrl={API_URL}
                token={token}
                initialData={editingAppointment}
                onAppointmentCreated={handleAppointmentCreated}
                onCancel={handleCloseForm}
              />
            </div>
          </div>
        )}

        {/* Filters and create button */}
        <section className="appointments-section">
          <div className="section-header">
            <h2>Appointments ({total})</h2>
            <button
              className="btn-submit btn-create"
              onClick={() => { setEditingAppointment(null); setShowForm(true) }}
            >
              + New Appointment
            </button>
          </div>

          <AppointmentFilters onApply={handleApplyFilters} onClear={handleClearFilters} />

          {/* Loading state */}
          {loading && <p className="loading">Loading appointments...</p>}

          {/* Error state */}
          {error && <div className="alert alert-error">{error}</div>}

          {/* Empty state */}
          {!loading && !error && appointments.length === 0 && (
            <div className="empty-state">
              <p>No appointments found. Create one to get started!</p>
            </div>
          )}

          {/* Appointments table */}
          {!loading && !error && appointments.length > 0 && (
            <>
              <div className="appointments-table-wrapper">
                <table className="appointments-table">
                  <thead>
                    <tr>
                      <th>Patient</th>
                      <th>Doctor</th>
                      <th>Specialty</th>
                      <th>Date / Time</th>
                      <th>Duration</th>
                      <th>Status</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {appointments.map((apt) => (
                      <tr key={apt.id}>
                        <td>
                          <div className="cell-primary">{apt.patient_name}</div>
                          <div className="cell-secondary">{apt.patient_email}</div>
                        </td>
                        <td>{apt.doctor_name}</td>
                        <td>{apt.specialty}</td>
                        <td>{formatDateTime(apt.appointment_date)}</td>
                        <td>{apt.duration_minutes} min</td>
                        <td>
                          <span
                            className="appointment-status-badge"
                            style={{
                              backgroundColor: STATUS_COLORS[apt.status] || '#6b7280',
                              color: 'white'
                            }}
                          >
                            {STATUS_LABELS[apt.status] || apt.status}
                          </span>
                        </td>
                        <td>
                          <div className="action-buttons">
                            <button
                              className="btn-action btn-action-edit"
                              onClick={() => handleEdit(apt)}
                              title="Edit"
                            >
                              Edit
                            </button>
                            {apt.status !== 'cancelled' && apt.status !== 'completed' && (
                              <button
                                className="btn-action btn-action-cancel"
                                onClick={() => handleCancel(apt.id)}
                                title="Cancel"
                              >
                                Cancel
                              </button>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="pagination">
                  <button
                    className="btn-page"
                    disabled={page <= 1}
                    onClick={() => setPage(p => p - 1)}
                  >
                    Previous
                  </button>
                  <span className="page-info">Page {page} of {totalPages}</span>
                  <button
                    className="btn-page"
                    disabled={page >= totalPages}
                    onClick={() => setPage(p => p + 1)}
                  >
                    Next
                  </button>
                </div>
              )}
            </>
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

export default AppointmentsPage
