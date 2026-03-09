import React from 'react'

const STATUS_COLORS = {
  scheduled: '#667eea',
  confirmed: '#4caf50',
  in_progress: '#ff9800',
  completed: '#2e7d32',
  cancelled: '#f44336',
  no_show: '#9e9e9e'
}

function AppointmentList({ appointments, onRefresh }) {
  if (!appointments || appointments.length === 0) {
    return (
      <div className="appointments-container">
        <button className="btn-refresh" onClick={onRefresh}>
          Refresh
        </button>
        <div className="empty-state">
          <p>No appointments found. Create one above!</p>
        </div>
      </div>
    )
  }

  return (
    <div className="appointments-container">
      <button className="btn-refresh" onClick={onRefresh}>
        Refresh
      </button>
      <div className="appointments-grid">
        {appointments.map((apt) => (
          <div key={apt.id} className="appointment-card">
            <div className="card-header">
              <h3>{apt.patient_name || 'Unknown Patient'}</h3>
              <span
                className="status-badge"
                style={{
                  backgroundColor: STATUS_COLORS[apt.status] || '#9e9e9e',
                  color: 'white'
                }}
              >
                {apt.status || 'unknown'}
              </span>
            </div>
            <div className="card-body">
              <p><strong>Doctor:</strong> {apt.doctor_name || 'N/A'}</p>
              <p><strong>Specialty:</strong> {apt.specialty || 'N/A'}</p>
              <p><strong>Date:</strong> {apt.appointment_date
                ? new Date(apt.appointment_date).toLocaleString()
                : 'N/A'}
              </p>
              {apt.duration_minutes && (
                <p><strong>Duration:</strong> {apt.duration_minutes} min</p>
              )}
              {apt.reason && (
                <p><strong>Reason:</strong> {apt.reason}</p>
              )}
            </div>
            <div className="card-footer">
              <p>ID: {apt.id?.substring(0, 8) || 'N/A'}...</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default AppointmentList
