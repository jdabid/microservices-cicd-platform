import React from 'react'

function PatientTable({ patients, onEdit, onDelete, loading }) {
  if (loading) {
    return (
      <div className="table-skeleton">
        {[1, 2, 3, 4, 5].map(i => (
          <div key={i} className="skeleton-row">
            <div className="skeleton-cell"></div>
            <div className="skeleton-cell"></div>
            <div className="skeleton-cell"></div>
            <div className="skeleton-cell skeleton-cell-short"></div>
            <div className="skeleton-cell skeleton-cell-short"></div>
            <div className="skeleton-cell skeleton-cell-short"></div>
          </div>
        ))}
      </div>
    )
  }

  if (!patients || patients.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">&#x1F465;</div>
        <h3>No patients found</h3>
        <p>Add your first patient to get started.</p>
      </div>
    )
  }

  return (
    <div className="table-responsive">
      <table className="patients-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Phone</th>
            <th>Gender</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {patients.map(patient => (
            <tr key={patient.id}>
              <td className="td-name">{patient.first_name} {patient.last_name}</td>
              <td>{patient.email}</td>
              <td>{patient.phone}</td>
              <td className="td-capitalize">{patient.gender}</td>
              <td>
                <span className={`patient-status-badge ${patient.is_active ? 'status-active' : 'status-inactive'}`}>
                  {patient.is_active ? 'Active' : 'Inactive'}
                </span>
              </td>
              <td className="td-actions">
                <button
                  className="btn-action btn-edit"
                  onClick={() => onEdit(patient)}
                  title="Edit patient"
                >
                  Edit
                </button>
                <button
                  className="btn-action btn-delete"
                  onClick={() => onDelete(patient)}
                  title="Delete patient"
                >
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default PatientTable
