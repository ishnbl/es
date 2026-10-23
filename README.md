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

Open http://localhost:5000 for the endpoint list. Set `PORT` to change the local
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

## Deploy with Gasper

This follows the build/run command approach in
[Gasper's Flask example](https://gasper-docs.netlify.app/examples/applications/python-flask/).

1. Push these project files to a Git repository accessible to your Gasper instance.
2. In `gasper-deploy.json`, replace the repository URL, branch, and application password.
3. Start Gasper and obtain a login token as described in its
   [quick start](https://gasper-docs.netlify.app/quick-start/).
4. Set your token and submit the deployment:

```sh
export GASPER_TOKEN='YOUR_LOGIN_TOKEN'
curl --fail-with-body -X POST http://localhost:3000/apps/python3 \
  -H "Authorization: Bearer $GASPER_TOKEN" \
  -H 'Content-Type: application/json' \
  --data-binary @gasper-deploy.json
```

Use `http://HOST_IP:CONTAINER_PORT/health` with the `host_ip` and `container_port`
from Gasper's response. The app listens inside the container on port 5000.
The Gasper Python image must provide Python 3.9+ for these dependencies.

Gasper manages its own infrastructure dependencies separately. This project
does not create or connect to a database. The deployment payload is based on
the documentation; an actual Gasper deployment has not been tested here.

## Tests

```sh
python -m unittest -v
```

Tests cover known calculation results, row pivoting, singular matrices,
repeatable Monte Carlo output, and invalid requests.
