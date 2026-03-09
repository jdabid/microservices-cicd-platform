import React from 'react'

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

function AppointmentList({ appointments, onRefresh, onEdit, onCancel }) {
  if (!appointments || appointments.length === 0) {
    return (
      <div className="appointments-container">
        {onRefresh && (
          <button className="btn-refresh" onClick={onRefresh}>
            Refresh
          </button>
        )}
        <div className="empty-state">
          <p>No appointments found. Create one above!</p>
        </div>
      </div>
    )
  }

  return (
    <div className="appointments-container">
      {onRefresh && (
        <button className="btn-refresh" onClick={onRefresh}>
          Refresh
        </button>
      )}
      <div className="appointments-grid">
        {appointments.map((apt) => (
          <div key={apt.id} className="appointment-card">
            <div className="card-header">
              <h3>{apt.patient_name || 'Unknown Patient'}</h3>
              <span
                className="appointment-status-badge"
                style={{
                  backgroundColor: STATUS_COLORS[apt.status] || '#6b7280',
                  color: 'white'
                }}
              >
                {STATUS_LABELS[apt.status] || apt.status || 'unknown'}
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
              {(onEdit || onCancel) && (
                <div className="card-actions">
                  {onEdit && (
                    <button
                      className="btn-action btn-action-edit"
                      onClick={() => onEdit(apt)}
                    >
                      Edit
                    </button>
                  )}
                  {onCancel && apt.status !== 'cancelled' && apt.status !== 'completed' && (
                    <button
                      className="btn-action btn-action-cancel"
                      onClick={() => onCancel(apt.id)}
                    >
                      Cancel
                    </button>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default AppointmentList
