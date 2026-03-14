/**
 * k6 load test: GET /api/v1/events (list with pagination)
 * Run: k6 run scripts/k6_load_events.js
 * With base URL: k6 run -e BASE_URL=http://localhost:8000 scripts/k6_load_events.js
 */
import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

export const options = {
  stages: [
    { duration: '30s', target: 10 },
    { duration: '1m', target: 20 },
    { duration: '30s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'],
    http_req_failed: ['rate<0.05'],
  },
};

export default function () {
  const res = http.get(`${BASE_URL}/api/v1/events?page=1&page_size=20`);
  check(res, {
    'status is 200': (r) => r.status === 200,
    'has items': (r) => {
      try {
        const body = JSON.parse(r.body);
        return Array.isArray(body.items) && typeof body.meta === 'object';
      } catch {
        return false;
      }
    },
  });
  sleep(0.5);
}
