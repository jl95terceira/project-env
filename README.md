# Introduction

A module to give to CLI tools support for persistent state / environment variables

Python version: >= **3.12**

# Getting around

- `project\package` - module path

- `pyproject.toml` - project metadata, with instructions for packaging

  See: https://hatch.pypa.io/latest/config/metadata/

*NB*: The reason why the package home directory `package` is under directory `project` is to avoid having to rework the directory structure if we decide to make a test module. In that case, the test module path shall be `project\tests`, we shall make `project` itself a module (via creating an empty `__init__.py` under it) and we shall use [`unittest`](https://docs.python.org/3/library/unittest.html#module-unittest).

# Build and install

Required:

- Python packages:

  - `hatch`
  - `build`

  These packages can be `pip`-installed. Example:

  ```
  pip install hatch
  ```

To build / pack up, run the following command at the top directory.

```
python -m build
```

A `.whl` is generated at directory `dist` which can then be `pip`-installed like so.

```
pip install dist\...whl
```

The package will be installed under the Python installation's `site-packages` to `jl95terceira\pytools`, in accordance with `pyproject.toml`.
