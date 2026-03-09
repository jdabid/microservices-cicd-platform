import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';
import { BASE_URL, API_PREFIX } from '../config/env.js';

// ---------- Custom metrics per flow ----------
const healthFlowErrors = new Rate('health_flow_errors');
const authFlowErrors = new Rate('auth_flow_errors');
const patientFlowErrors = new Rate('patient_flow_errors');
const appointmentFlowErrors = new Rate('appointment_flow_errors');

const healthFlowDuration = new Trend('health_flow_duration', true);
const authFlowDuration = new Trend('auth_flow_duration', true);
const patientFlowDuration = new Trend('patient_flow_duration', true);
const appointmentFlowDuration = new Trend('appointment_flow_duration', true);

const totalIterations = new Counter('total_iterations');

// ---------- URLs ----------
const AUTH_URL = `${BASE_URL}${API_PREFIX}/auth`;
const PATIENTS_URL = `${BASE_URL}${API_PREFIX}/patients`;
const APPOINTMENTS_URL = `${BASE_URL}${API_PREFIX}/appointments`;

export const options = {
  scenarios: {
    health_checks: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '1m', target: 8 },
        { duration: '3m', target: 8 },
        { duration: '1m', target: 0 },
      ],
      exec: 'healthFlow',
      tags: { flow: 'health' },
    },
    auth_operations: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '1m', target: 4 },
        { duration: '3m', target: 4 },
        { duration: '1m', target: 0 },
      ],
      exec: 'authFlow',
      tags: { flow: 'auth' },
    },
    patient_operations: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '1m', target: 4 },
        { duration: '3m', target: 4 },
        { duration: '1m', target: 0 },
      ],
      exec: 'patientFlow',
      tags: { flow: 'patient' },
    },
    appointment_operations: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '1m', target: 4 },
        { duration: '3m', target: 4 },
        { duration: '1m', target: 0 },
      ],
      exec: 'appointmentFlow',
      tags: { flow: 'appointment' },
    },
  },
  thresholds: {
    // Global thresholds
    http_req_duration: ['p(95)<500', 'p(99)<1000'],
    http_req_failed: ['rate<0.05'],
    // Per-flow thresholds
    health_flow_errors: ['rate<0.01'],
    auth_flow_errors: ['rate<0.05'],
    patient_flow_errors: ['rate<0.05'],
    appointment_flow_errors: ['rate<0.05'],
    health_flow_duration: ['p(95)<200'],
    auth_flow_duration: ['p(95)<500'],
    patient_flow_duration: ['p(95)<500'],
    appointment_flow_duration: ['p(95)<500'],
  },
};

// ---------- Helpers ----------
const FIRST_NAMES = ['Maria', 'Juan', 'Ana', 'Carlos', 'Sofia', 'Luis', 'Elena', 'Pedro'];
const LAST_NAMES = ['Garcia', 'Rodriguez', 'Martinez', 'Lopez', 'Hernandez', 'Gonzalez'];
const DOCTORS = ['Dr. Garcia', 'Dr. Martinez', 'Dr. Lopez', 'Dr. Rodriguez'];
const SPECIALTIES = ['General Medicine', 'Cardiology', 'Dermatology', 'Pediatrics'];

function randomItem(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

function uniqueId() {
  return `${__VU}-${__ITER}-${Date.now()}`;
}

function futureDate(daysAhead) {
  const date = new Date();
  date.setDate(date.getDate() + daysAhead);
  date.setHours(9 + Math.floor(Math.random() * 8), 0, 0, 0);
  return date.toISOString();
}

function registerAndLogin(prefix) {
  const email = `k6-full-${prefix}-${uniqueId()}@loadtest.com`;
  const password = 'K6TestPass1';
  const headers = { 'Content-Type': 'application/json' };

  http.post(
    `${AUTH_URL}/register`,
    JSON.stringify({ email, password, full_name: `K6 ${prefix} User` }),
    { headers }
  );

  const loginRes = http.post(
    `${AUTH_URL}/login`,
    JSON.stringify({ email, password }),
    { headers }
  );

  if (loginRes.status === 200) {
    return { token: loginRes.json('access_token'), email };
  }
  return { token: '', email };
}

// ---------- Flow: Health Checks (40% weight via VU allocation) ----------
export function healthFlow() {
  totalIterations.add(1);
  const start = Date.now();

  const healthRes = http.get(`${BASE_URL}/health`);
  const healthOk = check(healthRes, {
    'health: status 200': (r) => r.status === 200,
  });

  sleep(0.3);

  const readyRes = http.get(`${BASE_URL}/ready`);
  const readyOk = check(readyRes, {
    'ready: status 200': (r) => r.status === 200,
  });

  const ok = healthOk && readyOk;
  healthFlowErrors.add(!ok);
  healthFlowDuration.add(Date.now() - start);

  sleep(1);
}

// ---------- Flow: Auth Operations (20% weight) ----------
export function authFlow() {
  totalIterations.add(1);
  const start = Date.now();
  const headers = { 'Content-Type': 'application/json' };

  const email = `k6-fullauth-${uniqueId()}@loadtest.com`;
  const password = 'K6TestPass1';

  // Register
  const registerRes = http.post(
    `${AUTH_URL}/register`,
    JSON.stringify({ email, password, full_name: 'K6 Full Auth User' }),
    { headers }
  );

  const regOk = check(registerRes, {
    'auth: register 201': (r) => r.status === 201,
  });

  if (!regOk) {
    authFlowErrors.add(true);
    authFlowDuration.add(Date.now() - start);
    sleep(2);
    return;
  }

  sleep(0.3);

  // Login
  const loginRes = http.post(
    `${AUTH_URL}/login`,
    JSON.stringify({ email, password }),
    { headers }
  );

  const loginOk = check(loginRes, {
    'auth: login 200': (r) => r.status === 200,
    'auth: has token': (r) => r.json('access_token') !== undefined,
  });

  if (!loginOk) {
    authFlowErrors.add(true);
    authFlowDuration.add(Date.now() - start);
    sleep(2);
    return;
  }

  sleep(0.3);

  // Get profile
  const token = loginRes.json('access_token');
  const meRes = http.get(`${AUTH_URL}/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  const meOk = check(meRes, {
    'auth: me 200': (r) => r.status === 200,
  });

  authFlowErrors.add(!(regOk && loginOk && meOk));
  authFlowDuration.add(Date.now() - start);

  sleep(2);
}

// ---------- Flow: Patient Operations (20% weight) ----------
export function patientFlow() {
  totalIterations.add(1);
  const start = Date.now();
  const { token } = registerAndLogin('patient');

  if (!token) {
    patientFlowErrors.add(true);
    patientFlowDuration.add(Date.now() - start);
    sleep(2);
    return;
  }

  const headers = {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${token}`,
  };

  const id = uniqueId();

  // Create patient
  const createRes = http.post(
    PATIENTS_URL + '/',
    JSON.stringify({
      first_name: randomItem(FIRST_NAMES),
      last_name: randomItem(LAST_NAMES),
      email: `k6-fp-${id}@loadtest.com`,
      phone: '+15551234567',
      date_of_birth: '1985-03-20',
      gender: 'female',
    }),
    { headers }
  );

  const createOk = check(createRes, {
    'patient: create 201': (r) => r.status === 201,
  });

  if (!createOk) {
    patientFlowErrors.add(true);
    patientFlowDuration.add(Date.now() - start);
    sleep(2);
    return;
  }

  const patientId = createRes.json('id');
  sleep(0.3);

  // List patients
  const listRes = http.get(`${PATIENTS_URL}/?page=1&page_size=5`, { headers });
  check(listRes, { 'patient: list 200': (r) => r.status === 200 });

  sleep(0.3);

  // Get patient
  const getRes = http.get(`${PATIENTS_URL}/${patientId}`, { headers });
  const getOk = check(getRes, { 'patient: get 200': (r) => r.status === 200 });

  sleep(0.3);

  // Delete patient
  const delRes = http.del(`${PATIENTS_URL}/${patientId}`, null, { headers });
  const delOk = check(delRes, { 'patient: delete 200': (r) => r.status === 200 });

  patientFlowErrors.add(!(createOk && getOk && delOk));
  patientFlowDuration.add(Date.now() - start);

  sleep(2);
}

// ---------- Flow: Appointment Operations (20% weight) ----------
export function appointmentFlow() {
  totalIterations.add(1);
  const start = Date.now();
  const { token } = registerAndLogin('appointment');

  if (!token) {
    appointmentFlowErrors.add(true);
    appointmentFlowDuration.add(Date.now() - start);
    sleep(2);
    return;
  }

  const headers = {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${token}`,
  };

  const id = uniqueId();

  // Create appointment
  const createRes = http.post(
    APPOINTMENTS_URL + '/',
    JSON.stringify({
      patient_name: `K6 Patient ${id}`,
      patient_email: `k6-fa-${id}@loadtest.com`,
      doctor_name: randomItem(DOCTORS),
      specialty: randomItem(SPECIALTIES),
      appointment_date: futureDate(Math.floor(Math.random() * 30) + 1),
      duration_minutes: 30,
      reason: 'Load test appointment',
    }),
    { headers }
  );

  const createOk = check(createRes, {
    'appointment: create 201': (r) => r.status === 201,
  });

  if (!createOk) {
    appointmentFlowErrors.add(true);
    appointmentFlowDuration.add(Date.now() - start);
    sleep(2);
    return;
  }

  const appointmentId = createRes.json('id');
  sleep(0.3);

  // List appointments
  const listRes = http.get(`${APPOINTMENTS_URL}/?page=1&page_size=5`, { headers });
  check(listRes, { 'appointment: list 200': (r) => r.status === 200 });

  sleep(0.3);

  // Get appointment
  const getRes = http.get(`${APPOINTMENTS_URL}/${appointmentId}`, { headers });
  const getOk = check(getRes, { 'appointment: get 200': (r) => r.status === 200 });

  sleep(0.3);

  // Filter by status
  const filterRes = http.get(`${APPOINTMENTS_URL}/?status=scheduled`, { headers });
  check(filterRes, { 'appointment: filter 200': (r) => r.status === 200 });

  sleep(0.3);

  // Cancel appointment
  const cancelRes = http.del(`${APPOINTMENTS_URL}/${appointmentId}`, null, { headers });
  const cancelOk = check(cancelRes, {
    'appointment: cancel 200': (r) => r.status === 200,
    'appointment: status cancelled': (r) => r.json('status') === 'cancelled',
  });

  appointmentFlowErrors.add(!(createOk && getOk && cancelOk));
  appointmentFlowDuration.add(Date.now() - start);

  sleep(2);
}
