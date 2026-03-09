import React, { useState, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import axios from 'axios'
import { useAuth } from '../context/AuthContext'
import PatientTable from '../components/PatientTable'
import PatientForm from '../components/PatientForm'
import Pagination from '../components/Pagination'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function PatientsPage() {
  const { user, token, logout } = useAuth()

  const [patients, setPatients] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [successMsg, setSuccessMsg] = useState(null)

  // Pagination
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [total, setTotal] = useState(0)
  const pageSize = 10

  // Search
  const [search, setSearch] = useState('')
  const [searchInput, setSearchInput] = useState('')

  // Form state
  const [showForm, setShowForm] = useState(false)
  const [editingPatient, setEditingPatient] = useState(null)
  const [formLoading, setFormLoading] = useState(false)

  // Delete confirm
  const [deleteConfirm, setDeleteConfirm] = useState(null)

  const authHeaders = { Authorization: `Bearer ${token}` }

  const fetchPatients = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const params = {
        page: currentPage,
        page_size: pageSize,
        is_active: true
      }
      if (search.trim()) {
        params.search = search.trim()
      }
      const response = await axios.get(`${API_URL}/api/v1/patients/`, {
        headers: authHeaders,
        params
      })
      setPatients(response.data.items || [])
      setTotalPages(response.data.total_pages || 1)
      setTotal(response.data.total || 0)
    } catch (err) {
      console.error('Error fetching patients:', err)
      if (err.response?.status === 401) {
        logout()
        return
      }
      setError('Failed to load patients. Please try again.')
    } finally {
      setLoading(false)
    }
  }, [currentPage, search, token])

  useEffect(() => {
    fetchPatients()
  }, [fetchPatients])

  const clearMessages = () => {
    setError(null)
    setSuccessMsg(null)
  }

  const handleSearch = (e) => {
    e.preventDefault()
    setCurrentPage(1)
    setSearch(searchInput)
  }

  const handleClearSearch = () => {
    setSearchInput('')
    setSearch('')
    setCurrentPage(1)
  }

  const handlePageChange = (page) => {
    setCurrentPage(page)
  }

  const handleCreate = () => {
    clearMessages()
    setEditingPatient(null)
    setShowForm(true)
  }

  const handleEdit = (patient) => {
    clearMessages()
    setEditingPatient(patient)
    setShowForm(true)
  }

  const handleCancelForm = () => {
    setShowForm(false)
    setEditingPatient(null)
  }

  const handleSubmit = async (formData) => {
    try {
      setFormLoading(true)
      clearMessages()

      if (editingPatient) {
        await axios.put(
          `${API_URL}/api/v1/patients/${editingPatient.id}`,
          formData,
          { headers: authHeaders }
        )
        setSuccessMsg('Patient updated successfully.')
      } else {
        await axios.post(
          `${API_URL}/api/v1/patients/`,
          formData,
          { headers: authHeaders }
        )
        setSuccessMsg('Patient created successfully.')
      }

      setShowForm(false)
      setEditingPatient(null)
      fetchPatients()
    } catch (err) {
      console.error('Error saving patient:', err)
      if (err.response?.status === 401) {
        logout()
        return
      }
      const detail = err.response?.data?.detail
      if (typeof detail === 'string') {
        setError(detail)
      } else if (Array.isArray(detail)) {
        setError(detail.map(d => d.msg).join(', '))
      } else {
        setError('Failed to save patient. Please try again.')
      }
    } finally {
      setFormLoading(false)
    }
  }

  const handleDeleteClick = (patient) => {
    clearMessages()
    setDeleteConfirm(patient)
  }

  const handleDeleteConfirm = async () => {
    if (!deleteConfirm) return
    try {
      await axios.delete(
        `${API_URL}/api/v1/patients/${deleteConfirm.id}`,
        { headers: authHeaders }
      )
      setSuccessMsg('Patient deleted successfully.')
      setDeleteConfirm(null)
      fetchPatients()
    } catch (err) {
      console.error('Error deleting patient:', err)
      if (err.response?.status === 401) {
        logout()
        return
      }
      setError('Failed to delete patient. Please try again.')
      setDeleteConfirm(null)
    }
  }

  const handleDeleteCancel = () => {
    setDeleteConfirm(null)
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
      </header>

      <main className="App-main">
        <div className="page-breadcrumb">
          <Link to="/dashboard" className="breadcrumb-link">Dashboard</Link>
          <span className="breadcrumb-separator">/</span>
          <span className="breadcrumb-current">Patients</span>
        </div>

        {error && (
          <div className="alert alert-error">
            {error}
            <button className="alert-close" onClick={() => setError(null)}>&times;</button>
          </div>
        )}
        {successMsg && (
          <div className="alert alert-success">
            {successMsg}
            <button className="alert-close" onClick={() => setSuccessMsg(null)}>&times;</button>
          </div>
        )}

        <section className="patients-section">
          <div className="patients-header">
            <h2>Patients ({total})</h2>
            <button className="btn-submit btn-create-patient" onClick={handleCreate}>
              + New Patient
            </button>
          </div>

          <form className="search-bar" onSubmit={handleSearch}>
            <input
              type="text"
              className="search-input"
              placeholder="Search by name or email..."
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
            />
            <button type="submit" className="btn-search">Search</button>
            {search && (
              <button type="button" className="btn-clear-search" onClick={handleClearSearch}>
                Clear
              </button>
            )}
          </form>

          <PatientTable
            patients={patients}
            onEdit={handleEdit}
            onDelete={handleDeleteClick}
            loading={loading}
          />

          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={handlePageChange}
          />
        </section>

        {/* Form Modal */}
        {showForm && (
          <div className="modal-overlay" onClick={handleCancelForm}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h2>{editingPatient ? 'Edit Patient' : 'New Patient'}</h2>
                <button className="modal-close" onClick={handleCancelForm}>&times;</button>
              </div>
              <PatientForm
                initialData={editingPatient}
                onSubmit={handleSubmit}
                onCancel={handleCancelForm}
                loading={formLoading}
              />
            </div>
          </div>
        )}

        {/* Delete Confirm Dialog */}
        {deleteConfirm && (
          <div className="modal-overlay" onClick={handleDeleteCancel}>
            <div className="modal-content modal-confirm" onClick={(e) => e.stopPropagation()}>
              <h3>Confirm Delete</h3>
              <p>
                Are you sure you want to delete patient{' '}
                <strong>{deleteConfirm.first_name} {deleteConfirm.last_name}</strong>?
              </p>
              <div className="confirm-actions">
                <button className="btn-action btn-delete" onClick={handleDeleteConfirm}>
                  Delete
                </button>
                <button className="btn-cancel" onClick={handleDeleteCancel}>
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}
      </main>

      <footer className="App-footer">
        <p>Microservices CI/CD Platform - Portfolio Project</p>
        <p>Architecture: Vertical Slice + CQRS | Stack: FastAPI + React + Docker</p>
      </footer>
    </div>
  )
}

export default PatientsPage
