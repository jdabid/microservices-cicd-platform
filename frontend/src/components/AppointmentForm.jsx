import React, { useState, useEffect } from 'react'
import axios from 'axios'

const EMPTY_FORM = {
  patient_name: '',
  patient_email: '',
  patient_phone: '',
  doctor_name: '',
  specialty: '',
  appointment_date: '',
  duration_minutes: 30,
  reason: ''
}

function AppointmentForm({ apiUrl, token, initialData, onAppointmentCreated, onCancel }) {
  const isEditMode = !!initialData

  const [formData, setFormData] = useState(EMPTY_FORM)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    if (initialData) {
      setFormData({
        patient_name: initialData.patient_name || '',
        patient_email: initialData.patient_email || '',
        patient_phone: initialData.patient_phone || '',
        doctor_name: initialData.doctor_name || '',
        specialty: initialData.specialty || '',
        appointment_date: initialData.appointment_date
          ? initialData.appointment_date.slice(0, 16)
          : '',
        duration_minutes: initialData.duration_minutes || 30,
        reason: initialData.reason || ''
      })
    } else {
      setFormData(EMPTY_FORM)
    }
    setError(null)
    setSuccess(false)
  }, [initialData])

  const authHeaders = token ? { Authorization: `Bearer ${token}` } : {}

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setSuccess(false)

    try {
      const payload = {
        ...formData,
        duration_minutes: parseInt(formData.duration_minutes)
      }

      if (isEditMode) {
        await axios.put(
          `${apiUrl}/api/v1/appointments/${initialData.id}`,
          payload,
          { headers: authHeaders }
        )
      } else {
        await axios.post(
          `${apiUrl}/api/v1/appointments/`,
          payload,
          { headers: authHeaders }
        )
      }

      setSuccess(true)
      if (!isEditMode) {
        setFormData(EMPTY_FORM)
      }

      setTimeout(() => setSuccess(false), 3000)
      if (onAppointmentCreated) onAppointmentCreated()
    } catch (err) {
      console.error('Error saving appointment:', err)
      setError(err.response?.data?.detail || 'Failed to save appointment')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form className="appointment-form" onSubmit={handleSubmit}>
      {error && <div className="alert alert-error">{error}</div>}
      {success && (
        <div className="alert alert-success">
          Appointment {isEditMode ? 'updated' : 'created'} successfully!
        </div>
      )}

      <div className="form-row">
        <div className="form-group">
          <label htmlFor="patient_name">Patient Name *</label>
          <input
            type="text"
            id="patient_name"
            name="patient_name"
            value={formData.patient_name}
            onChange={handleChange}
            required
            placeholder="John Doe"
          />
        </div>

        <div className="form-group">
          <label htmlFor="patient_email">Email *</label>
          <input
            type="email"
            id="patient_email"
            name="patient_email"
            value={formData.patient_email}
            onChange={handleChange}
            required
            placeholder="john@example.com"
          />
        </div>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label htmlFor="patient_phone">Phone</label>
          <input
            type="tel"
            id="patient_phone"
            name="patient_phone"
            value={formData.patient_phone}
            onChange={handleChange}
            placeholder="+1 234 567 8900"
          />
        </div>

        <div className="form-group">
          <label htmlFor="doctor_name">Doctor Name *</label>
          <input
            type="text"
            id="doctor_name"
            name="doctor_name"
            value={formData.doctor_name}
            onChange={handleChange}
            required
            placeholder="Dr. Smith"
          />
        </div>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label htmlFor="specialty">Specialty *</label>
          <select
            id="specialty"
            name="specialty"
            value={formData.specialty}
            onChange={handleChange}
            required
          >
            <option value="">Select specialty...</option>
            <option value="General">General Medicine</option>
            <option value="Cardiology">Cardiology</option>
            <option value="Dermatology">Dermatology</option>
            <option value="Pediatrics">Pediatrics</option>
            <option value="Orthopedics">Orthopedics</option>
            <option value="Neurology">Neurology</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="duration_minutes">Duration (minutes) *</label>
          <input
            type="number"
            id="duration_minutes"
            name="duration_minutes"
            value={formData.duration_minutes}
            onChange={handleChange}
            min="15"
            max="240"
            step="15"
            required
          />
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="appointment_date">Appointment Date & Time *</label>
        <input
          type="datetime-local"
          id="appointment_date"
          name="appointment_date"
          value={formData.appointment_date}
          onChange={handleChange}
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="reason">Reason for Visit</label>
        <textarea
          id="reason"
          name="reason"
          value={formData.reason}
          onChange={handleChange}
          rows="3"
          placeholder="Describe the reason for the appointment..."
        />
      </div>

      <div className="form-button-row">
        <button type="submit" className="btn-submit" disabled={loading}>
          {loading
            ? 'Saving...'
            : isEditMode
              ? 'Update Appointment'
              : 'Create Appointment'
          }
        </button>
        {onCancel && (
          <button type="button" className="btn-cancel" onClick={onCancel}>
            Cancel
          </button>
        )}
      </div>
    </form>
  )
}

export default AppointmentForm
