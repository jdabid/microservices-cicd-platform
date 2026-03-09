import React, { useState } from 'react'

const STATUSES = [
  { value: '', label: 'All Statuses' },
  { value: 'scheduled', label: 'Scheduled' },
  { value: 'confirmed', label: 'Confirmed' },
  { value: 'cancelled', label: 'Cancelled' },
  { value: 'completed', label: 'Completed' },
  { value: 'no_show', label: 'No Show' }
]

function AppointmentFilters({ onApply, onClear }) {
  const [filters, setFilters] = useState({
    status: '',
    doctor_name: '',
    start_date: '',
    end_date: ''
  })

  const handleChange = (e) => {
    const { name, value } = e.target
    setFilters(prev => ({ ...prev, [name]: value }))
  }

  const handleApply = (e) => {
    e.preventDefault()
    const activeFilters = {}
    if (filters.status) activeFilters.status = filters.status
    if (filters.doctor_name.trim()) activeFilters.doctor_name = filters.doctor_name.trim()
    if (filters.start_date) activeFilters.start_date = filters.start_date
    if (filters.end_date) activeFilters.end_date = filters.end_date
    onApply(activeFilters)
  }

  const handleClear = () => {
    setFilters({ status: '', doctor_name: '', start_date: '', end_date: '' })
    onClear()
  }

  return (
    <form className="filters-bar" onSubmit={handleApply}>
      <div className="filter-group">
        <label htmlFor="filter-status">Status</label>
        <select
          id="filter-status"
          name="status"
          value={filters.status}
          onChange={handleChange}
        >
          {STATUSES.map(s => (
            <option key={s.value} value={s.value}>{s.label}</option>
          ))}
        </select>
      </div>

      <div className="filter-group">
        <label htmlFor="filter-doctor">Doctor</label>
        <input
          type="text"
          id="filter-doctor"
          name="doctor_name"
          value={filters.doctor_name}
          onChange={handleChange}
          placeholder="Doctor name..."
        />
      </div>

      <div className="filter-group">
        <label htmlFor="filter-start">From</label>
        <input
          type="date"
          id="filter-start"
          name="start_date"
          value={filters.start_date}
          onChange={handleChange}
        />
      </div>

      <div className="filter-group">
        <label htmlFor="filter-end">To</label>
        <input
          type="date"
          id="filter-end"
          name="end_date"
          value={filters.end_date}
          onChange={handleChange}
        />
      </div>

      <div className="filter-actions">
        <button type="submit" className="btn-filter-apply">Apply</button>
        <button type="button" className="btn-filter-clear" onClick={handleClear}>Clear</button>
      </div>
    </form>
  )
}

export default AppointmentFilters
