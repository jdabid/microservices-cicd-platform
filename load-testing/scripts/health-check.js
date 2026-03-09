import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';
import { BASE_URL } from '../config/env.js';

// Custom metrics
const healthErrors = new Rate('health_errors');
const healthDuration = new Trend('health_duration', true);
const readyDuration = new Trend('ready_duration', true);

export const options = {
  stages: [
    { duration: '30s', target: 10 },  // ramp up to 10 VUs
    { duration: '1m', target: 10 },   // hold at 10 VUs
    { duration: '30s', target: 0 },   // ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<200', 'p(99)<500'],
    http_req_failed: ['rate<0.01'],
    health_errors: ['rate<0.01'],
    health_duration: ['p(95)<200'],
    ready_duration: ['p(95)<200'],
  },
};

export default function () {
  // GET /health
  const healthRes = http.get(`${BASE_URL}/health`, {
    tags: { endpoint: 'health' },
  });

  check(healthRes, {
    'health: status is 200': (r) => r.status === 200,
    'health: response has status field': (r) => {
      const body = r.json();
      return body && body.status !== undefined;
    },
  });

  healthErrors.add(healthRes.status !== 200);
  healthDuration.add(healthRes.timings.duration);

  sleep(0.5);

  // GET /ready
  const readyRes = http.get(`${BASE_URL}/ready`, {
    tags: { endpoint: 'ready' },
  });

  check(readyRes, {
    'ready: status is 200': (r) => r.status === 200,
    'ready: response has status field': (r) => {
      const body = r.json();
      return body && body.status !== undefined;
    },
  });

  healthErrors.add(readyRes.status !== 200);
  readyDuration.add(readyRes.timings.duration);

  sleep(0.5);
}
