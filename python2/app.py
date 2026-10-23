"""Stateless compute API. All request data stays in memory for that request."""

from __future__ import division

import math
import os
import random
import statistics_compat as statistics
from timeit import default_timer

from flask import Flask, json, jsonify, render_template, request
from werkzeug.exceptions import HTTPException, UnsupportedMediaType

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app = Flask(__name__, template_folder=os.path.join(PROJECT_ROOT, 'templates'),
            static_folder=os.path.join(PROJECT_ROOT, 'static'))
app.config['MAX_CONTENT_LENGTH'] = 1000000


def body():
    if not request.is_json:
        raise UnsupportedMediaType('Send Content-Type: application/json.')
    data = request.get_json()
    if not isinstance(data, dict):
        raise ValueError('Send a JSON object.')
    return data


def numbers(value, limit=10000):
    if not isinstance(value, list) or not 1 <= len(value) <= limit:
        raise ValueError('Expected a list of 1 to {} numbers.'.format(limit))
    result = []
    for item in value:
        if type(item) not in (int, long, float):
            raise ValueError('Values must be finite numbers, not strings or booleans.')
        number = float(item)
        if not (not math.isnan(number) and not math.isinf(number)) or abs(number) > 1e100:
            raise ValueError('Numbers must be finite and have magnitude at most 1e100.')
        result.append(number)
    return result


@app.errorhandler(ValueError)
@app.errorhandler(OverflowError)
def invalid_input(error):
    return jsonify(error=str(error)), 400


@app.errorhandler(HTTPException)
def http_error(error):
    response = error.get_response()
    response.data = json.dumps({'error': error.description})
    response.content_type = 'application/json'
    return response


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/health', methods=['GET'])
def health():
    return jsonify(status='ok')


@app.route('/api/stats', methods=['POST'])
def stats():
    values = numbers(body().get('numbers'))
    return jsonify(
        count=len(values), sum=math.fsum(values), mean=statistics.mean(values),
        median=statistics.median(values), min=min(values), max=max(values),
        population_variance=statistics.pvariance(values),
        population_stddev=statistics.pstdev(values),
    )


@app.route('/api/solve', methods=['POST'])
def solve():
    """Solve Ax=b using Gaussian elimination with partial pivoting."""
    data = body()
    matrix = data.get('matrix')
    if not isinstance(matrix, list) or not 1 <= len(matrix) <= 20:
        raise ValueError('matrix must have 1 to 20 rows.')
    size = len(matrix)
    rows = [numbers(row, 20) for row in matrix]
    vector = numbers(data.get('vector'), 20)
    if any(len(row) != size for row in rows) or len(vector) != size:
        raise ValueError('matrix must be square and vector must match its size.')
    # Normalize each equation so the pivot tolerance is independent of units.
    for i, row in enumerate(rows):
        scale = max(abs(value) for value in row)
        if scale == 0:
            raise ValueError('Matrix has no unique solution.')
        rows[i] = [value / scale for value in row] + [vector[i] / scale]
    for col in xrange(size):
        pivot = max(xrange(col, size), key=lambda i: abs(rows[i][col]))
        if abs(rows[pivot][col]) < 1e-12:
            raise ValueError('Matrix is singular or too ill-conditioned to solve.')
        rows[col], rows[pivot] = rows[pivot], rows[col]
        for i in xrange(col + 1, size):
            factor = rows[i][col] / rows[col][col]
            for j in xrange(col, size + 1):
                rows[i][j] -= factor * rows[col][j]
    solution = [0.0] * size
    for i in xrange(size - 1, -1, -1):
        remainder = math.fsum(rows[i][j] * solution[j] for j in xrange(i + 1, size))
        solution[i] = (rows[i][size] - remainder) / rows[i][i]
    if not all((not math.isnan(value) and not math.isinf(value)) for value in solution):
        raise ValueError('Solution exceeds floating-point range.')
    return jsonify(solution=solution)


@app.route('/api/pi', methods=['POST'])
def estimate_pi():
    data = body()
    samples = data.get('samples', 100000)
    seed = data.get('seed', 42)
    if type(samples) not in (int, long) or not 1 <= samples <= 1000000:
        raise ValueError('samples must be an integer between 1 and 1000000.')
    if type(seed) not in (int, long) or not -(2**63) <= seed < 2**63:
        raise ValueError('seed must be a signed 64-bit integer.')
    rng = random.Random(seed)
    started = default_timer()
    inside = 0
    for _ in xrange(samples):
        x, y = rng.random(), rng.random()
        inside += x*x + y*y <= 1
    estimate = 4 * inside / samples
    return jsonify(
        samples=samples, seed=seed, estimate=estimate,
        absolute_error=abs(estimate - math.pi),
        elapsed_ms=round((default_timer() - started) * 1000, 3),
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', '8080')))
