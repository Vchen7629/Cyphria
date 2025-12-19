// Load test for 1000 users hitting frontend
import http from 'k6/http';
import { sleep } from 'k6';
import { check } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 50 },   // ramp up to 50 users
    { duration: '30s', target: 200 },    // stay at 50
    { duration: '30s', target: 500 },  // ramp up to 200
    { duration: '30s', target: 1000 },   // stay at 200
    { duration: '30s', target: 500 },  // ramp up to 500
    { duration: '1m', target: 500 },   // stay at 500
    { duration: '30s', target: 1000 }, // ramp up to 1000
    { duration: '1m', target: 1000 },  // stay at 1000
    { duration: '30s', target: 0 },    // ramp down
  ],
  thresholds: {
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<800'],
  },
};

export default function () {
  const res = http.get('https://www.cyphria.com');
  check(res, {
    'status was 200': (r) => r.status === 200,
  });
  sleep(1);
}
