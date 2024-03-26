# How to develop this package

## Publishing

We use [Poetry](https://python-poetry.org) to manage dependencies and publish this package to PyPI. Follow their instructions for setting up the `poetry` CLI.

Also make sure to [configure credentials](https://python-poetry.org) for PyPI. You can create an API token [here](https://pypi.org/manage/account/) (the credentials for logging in are in our shared 1password).

Once you have that set up, you can simply build and publish the package like so.

```sh
poetry build
poetry publish
```

Note that you need to bump the version in `pyproject.toml` before being able to publish a new version.
