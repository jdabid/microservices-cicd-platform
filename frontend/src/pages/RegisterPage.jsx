import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

function RegisterPage() {
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  const { register } = useAuth()
  const navigate = useNavigate()

  const passwordChecks = {
    length: password.length >= 8,
    uppercase: /[A-Z]/.test(password),
    lowercase: /[a-z]/.test(password),
    digit: /\d/.test(password)
  }

  const isPasswordValid = Object.values(passwordChecks).every(Boolean)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!isPasswordValid) {
      setError('Please meet all password requirements.')
      return
    }
    setError(null)
    setLoading(true)

    try {
      await register(email, password, fullName)
      navigate('/dashboard')
    } catch (err) {
      console.error('Registration failed:', err)
      const detail = err.response?.data?.detail
      if (typeof detail === 'string') {
        setError(detail)
      } else if (Array.isArray(detail)) {
        setError(detail.map(d => d.msg).join('. '))
      } else {
        setError('Registration failed. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1>Medical Appointments</h1>
          <p>Create your account</p>
        </div>

        <form className="auth-form" onSubmit={handleSubmit}>
          {error && <div className="alert alert-error">{error}</div>}

          <div className="form-group">
            <label htmlFor="fullName">Full Name</label>
            <input
              type="text"
              id="fullName"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
              placeholder="John Doe"
              autoComplete="name"
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="you@example.com"
              autoComplete="email"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="Create a strong password"
              autoComplete="new-password"
            />
            <div className="password-requirements">
              <p className={passwordChecks.length ? 'met' : ''}>
                {passwordChecks.length ? '\u2713' : '\u2022'} At least 8 characters
              </p>
              <p className={passwordChecks.uppercase ? 'met' : ''}>
                {passwordChecks.uppercase ? '\u2713' : '\u2022'} One uppercase letter
              </p>
              <p className={passwordChecks.lowercase ? 'met' : ''}>
                {passwordChecks.lowercase ? '\u2713' : '\u2022'} One lowercase letter
              </p>
              <p className={passwordChecks.digit ? 'met' : ''}>
                {passwordChecks.digit ? '\u2713' : '\u2022'} One digit
              </p>
            </div>
          </div>

          <button
            type="submit"
            className="btn-submit btn-auth"
            disabled={loading || !isPasswordValid}
          >
            {loading ? 'Creating account...' : 'Create Account'}
          </button>
        </form>

        <div className="auth-footer">
          <p>Already have an account? <Link to="/login">Sign in</Link></p>
        </div>
      </div>
    </div>
  )
}

export default RegisterPage
