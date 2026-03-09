import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend } from 'k6/metrics';
import { BASE_URL, API_PREFIX } from '../config/env.js';

// Custom metrics
const patientErrors = new Rate('patient_errors');
const createPatientDuration = new Trend('create_patient_duration', true);
const getPatientDuration = new Trend('get_patient_duration', true);
const listPatientsDuration = new Trend('list_patients_duration', true);
const updatePatientDuration = new Trend('update_patient_duration', true);
const deletePatientDuration = new Trend('delete_patient_duration', true);

const AUTH_URL = `${BASE_URL}${API_PREFIX}/auth`;
const PATIENTS_URL = `${BASE_URL}${API_PREFIX}/patients`;

export const options = {
  stages: [
    { duration: '30s', target: 5 },   // ramp up to 5 VUs
    { duration: '2m', target: 5 },    // hold at 5 VUs
    { duration: '30s', target: 0 },   // ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'],
    http_req_failed: ['rate<0.05'],
    patient_errors: ['rate<0.05'],
    create_patient_duration: ['p(95)<500'],
    get_patient_duration: ['p(95)<500'],
    list_patients_duration: ['p(95)<500'],
    update_patient_duration: ['p(95)<500'],
    delete_patient_duration: ['p(95)<500'],
  },
};

const FIRST_NAMES = ['Maria', 'Juan', 'Ana', 'Carlos', 'Sofia', 'Luis', 'Elena', 'Pedro', 'Laura', 'Miguel'];
const LAST_NAMES = ['Garcia', 'Rodriguez', 'Martinez', 'Lopez', 'Hernandez', 'Gonzalez', 'Perez', 'Sanchez', 'Ramirez', 'Torres'];
const GENDERS = ['male', 'female', 'other'];

function randomItem(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

function generatePatientData() {
  const id = `${__VU}-${__ITER}-${Date.now()}`;
  return {
    first_name: randomItem(FIRST_NAMES),
    last_name: randomItem(LAST_NAMES),
    email: `k6-patient-${id}@loadtest.com`,
    phone: `+1${Math.floor(Math.random() * 9000000000 + 1000000000)}`,
    date_of_birth: '1990-05-15',
    gender: randomItem(GENDERS),
    address: `${Math.floor(Math.random() * 9999)} Test Street, Suite ${Math.floor(Math.random() * 100)}`,
  };
}

// Setup: register and login to get auth token
export function setup() {
  const email = `k6-patients-setup-${Date.now()}@loadtest.com`;
  const password = 'K6TestPass1';
  const headers = { 'Content-Type': 'application/json' };

  // Register
  const registerRes = http.post(
    `${AUTH_URL}/register`,
    JSON.stringify({ email, password, full_name: 'K6 Patient Test Setup' }),
    { headers }
  );

  if (registerRes.status !== 201) {
    console.warn(`Setup register failed: ${registerRes.status} - ${registerRes.body}`);
  }

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

  let patientId;

  // 1. Create a patient
  group('Create Patient', function () {
    const patientData = generatePatientData();
    const createRes = http.post(PATIENTS_URL + '/', JSON.stringify(patientData), {
      headers,
      tags: { endpoint: 'create_patient' },
    });

    const ok = check(createRes, {
      'create: status is 201': (r) => r.status === 201,
      'create: returns patient id': (r) => r.json('id') !== undefined,
      'create: returns correct first_name': (r) => r.json('first_name') === patientData.first_name,
    });

    patientErrors.add(!ok);
    createPatientDuration.add(createRes.timings.duration);

    if (ok) {
      patientId = createRes.json('id');
    }
  });

  if (!patientId) {
    sleep(1);
    return;
  }

  sleep(0.5);

  // 2. Get patient by ID
  group('Get Patient', function () {
    const getRes = http.get(`${PATIENTS_URL}/${patientId}`, {
      headers,
      tags: { endpoint: 'get_patient' },
    });

    const ok = check(getRes, {
      'get: status is 200': (r) => r.status === 200,
      'get: returns correct id': (r) => r.json('id') === patientId,
      'get: is_active is true': (r) => r.json('is_active') === true,
    });

    patientErrors.add(!ok);
    getPatientDuration.add(getRes.timings.duration);
  });

  sleep(0.5);

  // 3. List patients
  group('List Patients', function () {
    const listRes = http.get(`${PATIENTS_URL}/?page=1&page_size=10`, {
      headers,
      tags: { endpoint: 'list_patients' },
    });

    const ok = check(listRes, {
      'list: status is 200': (r) => r.status === 200,
      'list: returns items array': (r) => Array.isArray(r.json('items')),
      'list: returns total count': (r) => r.json('total') !== undefined,
      'list: returns pagination': (r) => r.json('page') !== undefined && r.json('total_pages') !== undefined,
    });

    patientErrors.add(!ok);
    listPatientsDuration.add(listRes.timings.duration);
  });

  sleep(0.5);

  // 4. Update patient
  group('Update Patient', function () {
    const updatePayload = JSON.stringify({
      phone: `+1${Math.floor(Math.random() * 9000000000 + 1000000000)}`,
      address: `${Math.floor(Math.random() * 9999)} Updated Avenue`,
    });

    const updateRes = http.put(`${PATIENTS_URL}/${patientId}`, updatePayload, {
      headers,
      tags: { endpoint: 'update_patient' },
    });

    const ok = check(updateRes, {
      'update: status is 200': (r) => r.status === 200,
      'update: returns correct id': (r) => r.json('id') === patientId,
    });

    patientErrors.add(!ok);
    updatePatientDuration.add(updateRes.timings.duration);
  });

  sleep(0.5);

  // 5. Delete (soft-delete) patient
  group('Delete Patient', function () {
    const deleteRes = http.del(`${PATIENTS_URL}/${patientId}`, null, {
      headers,
      tags: { endpoint: 'delete_patient' },
    });

    const ok = check(deleteRes, {
      'delete: status is 200': (r) => r.status === 200,
      'delete: patient is inactive': (r) => r.json('is_active') === false,
    });

    patientErrors.add(!ok);
    deletePatientDuration.add(deleteRes.timings.duration);
  });

  sleep(1);
}
