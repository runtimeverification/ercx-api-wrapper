# ERCx API Python Wrapper

This Python wrapper provides easier access to [ERCx Open API](https://ercx.runtimeverification.com/open-api).

The wrapper uses the `requests` package.

We use `poetry` as build system.

To install the wrapper:
1. Make sure you have Python install: `python --version`.
2. Install `poetry`using `pip`: `pip install poetry`.
3. Verify the installation: `poetry --version`.
4. Install and create a virtual environment for running the wrapper:
```
poetry install
poetry shell
```

To run the wrapper: 
1. Generate an API key using the [API page](https://ercx.runtimeverification.com/open-api). Note, for this you need to create an account and login first.
2. Input the API key in `config.ini`.
3. Tweak and run the examples in `api.py`.

```
python api.py
```