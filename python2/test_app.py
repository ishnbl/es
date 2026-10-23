import unittest

from app import app


class ComputeTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_statistics(self):
        response = self.client.post('/api/stats', json={'numbers': [1, 2, 3, 4]})
        self.assertEqual(response.status_code, 200)
        result = response.get_json()
        self.assertEqual(result['mean'], 2.5)
        self.assertEqual(result['median'], 2.5)
        self.assertEqual(result['population_variance'], 1.25)
        self.assertEqual(result['sum'], 10)

    def test_solver_pivots_rows(self):
        response = self.client.post('/api/solve', json={
            'matrix': [[0, 2], [1, 1]], 'vector': [4, 5]})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['solution'], [3, 2])

    def test_solver_rejects_singular_matrix(self):
        response = self.client.post('/api/solve', json={
            'matrix': [[1, 2], [2, 4]], 'vector': [3, 6]})
        self.assertEqual(response.status_code, 400)

    def test_pi_estimate(self):
        payload = {'samples': 100000, 'seed': 42}
        first = self.client.post('/api/pi', json=payload)
        second = self.client.post('/api/pi', json=payload)
        self.assertEqual(first.status_code, 200)
        self.assertEqual(first.get_json()['estimate'], second.get_json()['estimate'])
        self.assertAlmostEqual(first.get_json()['estimate'], 3.14159, delta=0.03)

    def test_invalid_inputs(self):
        cases = [
            ('/api/stats', {'numbers': []}),
            ('/api/stats', {'numbers': [True]}),
            ('/api/stats', {'numbers': [float('inf')]}),
            ('/api/stats', {'numbers': [1e308, 1e308]}),
            ('/api/solve', {'matrix': [[1, 2]], 'vector': [1]}),
            ('/api/solve', {'matrix': [[1]], 'vector': []}),
            ('/api/pi', {'samples': 0}),
            ('/api/pi', {'samples': 1000001}),
            ('/api/pi', {'samples': 1.5}),
            ('/api/pi', {'seed': []}),
            ('/api/pi', []),
        ]
        for route, payload in cases:
            response = self.client.post(route, json=payload)
            self.assertEqual(response.status_code, 400)
            self.assertIn('error', response.get_json())

    def test_http_errors_are_json(self):
        response = self.client.post('/api/stats', data='{', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.get_json())
        self.assertEqual(self.client.get('/health').get_json()['status'], 'ok')
        self.assertEqual(self.client.get('/missing').status_code, 404)


if __name__ == '__main__':
    unittest.main()
