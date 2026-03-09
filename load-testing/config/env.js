/**
 * Environment configuration for k6 load tests.
 *
 * Override defaults via environment variables:
 *   k6 run -e BASE_URL=https://staging.example.com scripts/health-check.js
 */

export const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
export const API_PREFIX = '/api/v1';

// Test user credentials (used by auth-dependent tests)
export const TEST_USER_EMAIL = __ENV.TEST_USER_EMAIL || `k6-loadtest-${Date.now()}@test.com`;
export const TEST_USER_PASSWORD = __ENV.TEST_USER_PASSWORD || 'K6LoadTest1';
export const TEST_USER_NAME = __ENV.TEST_USER_NAME || 'K6 Load Test User';
