# Compute lab

A small Python Flask API for testing deployments and HTTP requests. It computes
statistics, solves linear equations, and estimates pi using Monte Carlo sampling.
No database, ORM, external API, credentials, or persistent storage is used by the app.
Requests are independent, so restarting the app loses no application data.

## Run locally

Use Python 3.9 or newer. Dependencies are Flask and Gunicorn, with Python's standard
library doing the calculations.

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open http://localhost:5000 for the API tester. Each endpoint has a form with
example inputs and displays its response, HTTP status, and request duration. Set `PORT` to change the local
port. For a deployment-style run on Linux:

```sh
gunicorn --bind 0.0.0.0:5000 --workers 2 --access-logfile - app:app
```

## Try the computations

```sh
curl http://localhost:5000/health

curl http://localhost:5000/api/stats \
  -H 'Content-Type: application/json' \
  -d '{"numbers": [1, 2, 3, 4]}'

curl http://localhost:5000/api/solve \
  -H 'Content-Type: application/json' \
  -d '{"matrix": [[2, 1], [1, -1]], "vector": [5, 1]}'

curl http://localhost:5000/api/pi \
  -H 'Content-Type: application/json' \
  -d '{"samples": 100000, "seed": 42}'
```

The statistics example returns mean and median 2.5, sum 10, and population variance
1.25. The solver returns `{"solution": [2.0, 1.0]}` for the equations
`2x + y = 5` and `x - y = 1`. The pi estimate is approximate; using the same seed
and sample count repeats the result. `elapsed_ms` measures computation time.

For a heavier CPU request, set `samples` to `1000000`. Requests run synchronously,
so simultaneous computations can occupy both Gunicorn workers.

Input limits: 10,000 statistics values, a 20 by 20 matrix, 1,000,000 Monte Carlo
samples, and a 1 MB request body. Numeric inputs must be finite and have magnitude
at most `1e100`. Statistics use population variance. The solver rejects singular
matrices and normalized pivots below `1e-12`; it is a small floating-point demo,
not a scientific linear algebra package. Bad inputs return JSON errors with
HTTP 400; oversized bodies return 413 and non-JSON requests return 415.

## Deploy

Install `requirements.txt` and use this start command on your hosting service:

```sh
gunicorn --bind "0.0.0.0:${PORT:-5000}" --workers 2 --access-logfile - app:app
```

Use Python 3.9 or newer. Include the `templates/` and `static/` directories when
deploying. The HTML page and API share the same server, with no frontend build
step or database setup. `GET /health` is available for health checks.

## Tests

```sh
python -m unittest -v
```

Tests cover known calculation results, row pivoting, singular matrices,
repeatable Monte Carlo output, and invalid requests.
