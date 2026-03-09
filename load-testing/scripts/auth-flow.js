import http from 'k6/http';
import { check, sleep, fail } from 'k6';
import { Rate, Trend } from 'k6/metrics';
import { SharedArray } from 'k6/data';
import { BASE_URL, API_PREFIX } from '../config/env.js';

// Custom metrics
const authErrors = new Rate('auth_errors');
const registerDuration = new Trend('register_duration', true);
const loginDuration = new Trend('login_duration', true);
const meDuration = new Trend('me_duration', true);

const AUTH_URL = `${BASE_URL}${API_PREFIX}/auth`;

export const options = {
  stages: [
    { duration: '30s', target: 5 },   // ramp up to 5 VUs
    { duration: '1m', target: 5 },    // hold at 5 VUs
    { duration: '30s', target: 0 },   // ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'],
    http_req_failed: ['rate<0.05'],
    auth_errors: ['rate<0.05'],
    register_duration: ['p(95)<500'],
    login_duration: ['p(95)<500'],
    me_duration: ['p(95)<500'],
  },
};

function generateUniqueEmail() {
  const id = `${__VU}-${__ITER}-${Date.now()}`;
  return `k6-auth-${id}@loadtest.com`;
}

export default function () {
  const email = generateUniqueEmail();
  const password = 'K6TestPass1';
  const fullName = `K6 Auth User ${__VU}-${__ITER}`;

  const headers = { 'Content-Type': 'application/json' };

  // 1. Register a new user
  const registerPayload = JSON.stringify({
    email: email,
    password: password,
    full_name: fullName,
  });

  const registerRes = http.post(`${AUTH_URL}/register`, registerPayload, {
    headers,
    tags: { endpoint: 'register' },
  });

  const registerOk = check(registerRes, {
    'register: status is 201': (r) => r.status === 201,
    'register: returns user id': (r) => r.json('id') !== undefined,
    'register: returns correct email': (r) => r.json('email') === email,
  });

  authErrors.add(!registerOk);
  registerDuration.add(registerRes.timings.duration);

  if (!registerOk) {
    console.warn(`Register failed: ${registerRes.status} - ${registerRes.body}`);
    sleep(1);
    return;
  }

  sleep(0.5);

  // 2. Login to get JWT token
  const loginPayload = JSON.stringify({
    email: email,
    password: password,
  });

  const loginRes = http.post(`${AUTH_URL}/login`, loginPayload, {
    headers,
    tags: { endpoint: 'login' },
  });

  const loginOk = check(loginRes, {
    'login: status is 200': (r) => r.status === 200,
    'login: returns access_token': (r) => r.json('access_token') !== undefined,
    'login: token_type is bearer': (r) => r.json('token_type') === 'bearer',
  });

  authErrors.add(!loginOk);
  loginDuration.add(loginRes.timings.duration);

  if (!loginOk) {
    console.warn(`Login failed: ${loginRes.status} - ${loginRes.body}`);
    sleep(1);
    return;
  }

  const token = loginRes.json('access_token');

  sleep(0.5);

  // 3. Get current user profile
  const meRes = http.get(`${AUTH_URL}/me`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
    tags: { endpoint: 'me' },
  });

  const meOk = check(meRes, {
    'me: status is 200': (r) => r.status === 200,
    'me: returns correct email': (r) => r.json('email') === email,
    'me: returns full_name': (r) => r.json('full_name') === fullName,
  });

  authErrors.add(!meOk);
  meDuration.add(meRes.timings.duration);

  sleep(1);
}
