import React, { useState } from 'react'
import axios from 'axios'

function AppointmentForm({ apiUrl, onAppointmentCreated }) {
  const [formData, setFormData] = useState({
    patient_name: '',
    patient_email: '',
    patient_phone: '',
    doctor_name: '',
    specialty: '',
    appointment_date: '',
    duration_minutes: 30,
    reason: ''
  })

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(false)

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
      await axios.post(`${apiUrl}/api/v1/appointments/`, {
        ...formData,
        duration_minutes: parseInt(formData.duration_minutes)
      })

      setSuccess(true)
      setFormData({
        patient_name: '',
        patient_email: '',
        patient_phone: '',
        doctor_name: '',
        specialty: '',
        appointment_date: '',
        duration_minutes: 30,
        reason: ''
      })

      setTimeout(() => setSuccess(false), 3000)
      onAppointmentCreated()
    } catch (err) {
      console.error('Error creating appointment:', err)
      setError(err.response?.data?.detail || 'Failed to create appointment')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form className="appointment-form" onSubmit={handleSubmit}>
      {error && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">✅ Appointment created successfully!</div>}

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

      <button type="submit" className="btn-submit" disabled={loading}>
        {loading ? '⏳ Creating...' : '✅ Create Appointment'}
      </button>
    </form>
  )
}

export default AppointmentForm