# Python 2 compute lab

Python 2.7 version of the same API. The frontend is in `templates/` and `static/`.
Select the `python2` branch when deploying this repository.
No database or persistent storage is used.

From the repository root, use these deployment settings:

- Runtime: Python 2.7
- Index file: `app.py`
- Port: `8080`
- Build command: `python2 -m pip install -r requirements.txt`
- Run command: `gunicorn --bind 0.0.0.0:8080 --workers 2 --access-logfile - --error-logfile - app:app`

If the runtime names its Python 2 executable `python`, replace `python2` with
`python` in the build command. The `gunicorn` executable must come from the Python 2 environment. Check `python --version` first.

For local development:

```sh
python2 -m pip install -r requirements.txt
python2 app.py
```

Open http://localhost:8080 to use the forms. API paths and payloads match the
Python 3 version. Input errors return JSON. `PORT` changes the development
server port, and the Gunicorn command binds explicitly to 8080.

Run the tests from the repository root:

```sh
python2 -m unittest -v test_app
```

Python 2 and these legacy dependencies are unsupported. This variant is for
testing a Python 2 deployment environment.
