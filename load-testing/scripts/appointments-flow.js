import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend } from 'k6/metrics';
import { BASE_URL, API_PREFIX } from '../config/env.js';

// Custom metrics
const appointmentErrors = new Rate('appointment_errors');
const createAppointmentDuration = new Trend('create_appointment_duration', true);
const getAppointmentDuration = new Trend('get_appointment_duration', true);
const listAppointmentsDuration = new Trend('list_appointments_duration', true);
const filterAppointmentsDuration = new Trend('filter_appointments_duration', true);
const cancelAppointmentDuration = new Trend('cancel_appointment_duration', true);

const AUTH_URL = `${BASE_URL}${API_PREFIX}/auth`;
const APPOINTMENTS_URL = `${BASE_URL}${API_PREFIX}/appointments`;

export const options = {
  stages: [
    { duration: '30s', target: 5 },   // ramp up to 5 VUs
    { duration: '2m', target: 5 },    // hold at 5 VUs
    { duration: '30s', target: 0 },   // ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'],
    http_req_failed: ['rate<0.05'],
    appointment_errors: ['rate<0.05'],
    create_appointment_duration: ['p(95)<500'],
    get_appointment_duration: ['p(95)<500'],
    list_appointments_duration: ['p(95)<500'],
    filter_appointments_duration: ['p(95)<500'],
    cancel_appointment_duration: ['p(95)<500'],
  },
};

const DOCTORS = ['Dr. Garcia', 'Dr. Martinez', 'Dr. Lopez', 'Dr. Rodriguez', 'Dr. Hernandez'];
const SPECIALTIES = ['General Medicine', 'Cardiology', 'Dermatology', 'Pediatrics', 'Orthopedics'];
const REASONS = ['Annual checkup', 'Follow-up visit', 'New symptoms', 'Prescription renewal', 'Lab results review'];

function randomItem(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

function futureDate(daysAhead) {
  const date = new Date();
  date.setDate(date.getDate() + daysAhead);
  date.setHours(9 + Math.floor(Math.random() * 8), 0, 0, 0);
  return date.toISOString();
}

function generateAppointmentData() {
  const id = `${__VU}-${__ITER}-${Date.now()}`;
  return {
    patient_name: `K6 Patient ${id}`,
    patient_email: `k6-apt-patient-${id}@loadtest.com`,
    patient_phone: `+1${Math.floor(Math.random() * 9000000000 + 1000000000)}`,
    doctor_name: randomItem(DOCTORS),
    specialty: randomItem(SPECIALTIES),
    appointment_date: futureDate(Math.floor(Math.random() * 30) + 1),
    duration_minutes: [15, 30, 45, 60][Math.floor(Math.random() * 4)],
    reason: randomItem(REASONS),
    notes: `Load test appointment created by VU ${__VU}`,
  };
}

// Setup: register and login to get auth token
export function setup() {
  const email = `k6-appointments-setup-${Date.now()}@loadtest.com`;
  const password = 'K6TestPass1';
  const headers = { 'Content-Type': 'application/json' };

  // Register
  http.post(
    `${AUTH_URL}/register`,
    JSON.stringify({ email, password, full_name: 'K6 Appointments Test Setup' }),
    { headers }
  );

  // Login
  const loginRes = http.post(
    `${AUTH_URL}/login`,
    JSON.stringify({ email, password }),
    { headers }
  );

  if (loginRes.status !== 200) {
    console.error(`Setup login failed: ${loginRes.status} - ${loginRes.body}`);
    return { token: '' };
  }

  return { token: loginRes.json('access_token') };
}

export default function (data) {
  const headers = {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${data.token}`,
  };

  let appointmentId;

  // 1. Create appointment
  group('Create Appointment', function () {
    const appointmentData = generateAppointmentData();
    const createRes = http.post(
      APPOINTMENTS_URL + '/',
      JSON.stringify(appointmentData),
      { headers, tags: { endpoint: 'create_appointment' } }
    );

    const ok = check(createRes, {
      'create: status is 201': (r) => r.status === 201,
      'create: returns appointment id': (r) => r.json('id') !== undefined,
      'create: status is scheduled': (r) => r.json('status') === 'scheduled',
    });

    appointmentErrors.add(!ok);
    createAppointmentDuration.add(createRes.timings.duration);

    if (ok) {
      appointmentId = createRes.json('id');
    }
  });

  if (!appointmentId) {
    sleep(1);
    return;
  }

  sleep(0.5);

  // 2. List appointments
  group('List Appointments', function () {
    const listRes = http.get(`${APPOINTMENTS_URL}/?page=1&page_size=10`, {
      headers,
      tags: { endpoint: 'list_appointments' },
    });

    const ok = check(listRes, {
      'list: status is 200': (r) => r.status === 200,
      'list: returns items array': (r) => Array.isArray(r.json('items')),
      'list: returns total count': (r) => r.json('total') !== undefined,
      'list: returns pagination': (r) => r.json('page') !== undefined,
    });

    appointmentErrors.add(!ok);
    listAppointmentsDuration.add(listRes.timings.duration);
  });

  sleep(0.5);

  // 3. Get appointment by ID
  group('Get Appointment', function () {
    const getRes = http.get(`${APPOINTMENTS_URL}/${appointmentId}`, {
      headers,
      tags: { endpoint: 'get_appointment' },
    });

    const ok = check(getRes, {
      'get: status is 200': (r) => r.status === 200,
      'get: returns correct id': (r) => r.json('id') === appointmentId,
      'get: has doctor_name': (r) => r.json('doctor_name') !== undefined,
    });

    appointmentErrors.add(!ok);
    getAppointmentDuration.add(getRes.timings.duration);
  });

  sleep(0.5);

  // 4. Filter appointments by status
  group('Filter Appointments', function () {
    const filterRes = http.get(`${APPOINTMENTS_URL}/?status=scheduled&page=1&page_size=5`, {
      headers,
      tags: { endpoint: 'filter_appointments' },
    });

    const ok = check(filterRes, {
      'filter: status is 200': (r) => r.status === 200,
      'filter: returns items': (r) => Array.isArray(r.json('items')),
      'filter: all items are scheduled': (r) => {
        const items = r.json('items');
        return items.every((item) => item.status === 'scheduled');
      },
    });

    appointmentErrors.add(!ok);
    filterAppointmentsDuration.add(filterRes.timings.duration);
  });

  sleep(0.5);

  // 5. Cancel appointment
  group('Cancel Appointment', function () {
    const cancelRes = http.del(`${APPOINTMENTS_URL}/${appointmentId}`, null, {
      headers,
      tags: { endpoint: 'cancel_appointment' },
    });

    const ok = check(cancelRes, {
      'cancel: status is 200': (r) => r.status === 200,
      'cancel: status is cancelled': (r) => r.json('status') === 'cancelled',
    });

    appointmentErrors.add(!ok);
    cancelAppointmentDuration.add(cancelRes.timings.duration);
  });

  sleep(1);
}
