# Runnable Family

![GitHub top language](https://img.shields.io/github/languages/top/hmasdev/runnable_family)
![GitHub tag (latest SemVer)](https://img.shields.io/github/v/tag/hmasdev/runnable_family?sort=semver)
![GitHub](https://img.shields.io/github/license/hmasdev/runnable_family)
![GitHub last commit](https://img.shields.io/github/last-commit/hmasdev/runnable_family)

![Scheduled Test](https://github.com/hmasdev/runnable_family/actions/workflows/tests-on-schedule.yaml/badge.svg)

A python library implementing a family of Runnables in langchain like loopback, self-consistent, self-refine, and self-translate.

## Requirements

- Python 3.10 or higher

See the [pyproject.toml](./pyproject.toml) file for the required packages.

## Installation

First, you should create a virtual environment before installing the package.

- On Unix or MacOS:

  ```bash
  python -m venv venv
  source venv/bin/activate
  ```

- On Windows:

  ```bash
  python -m venv venv
  venv\Scripts\activate
  ```

After creating the virtual environment, you can install the package using pip:

```bash
pip install git+https://github.com/hmasdev/runnable_family
```

or you can clone the repository and install the package using pip:

```bash
git clone https://github.com/hmasdev/runnable_family
cd runnable_family
pip install .
```

## Usage

Just import your favorite classes.

```python
from runnable_family.basic import RunnableConstant, RunnableAdd, RunnablePartialLambda, RunnableLog
from runnable_family.loopback import RunnableLoopback
from runnable_family.gacha import RunnableGacha
from runnable_family.random import RunnableRandomBranch
from runnable_family.runnable_diff import RunnableDiff
from runnable_family.self_consistent import RunnableSelfConsistent
from runnable_family.self_refine import RunnableSelfRefine
from runnable_family.self_translate import RunnableSelfTranslate
```

They are inherited from the Runnable class, so you can use them as a Runnable, that is, you can use them as chain components.

See [basic-examples.ipynb](./examples/basic-examples.ipynb) to see how to use them.

## Development

1. Fork the repository: [https://github.com/hmasdev/runnable_family](https://github.com/hmasdev/runnable_family)
2. Clone the repository

   ```bash
   git clone https://github.com/{YOURE_NAME}/runnable_family
   cd runnable_family
   ```

3. Create a virtual environment

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

4. Install the required packages

   ```bash
   pip install -e .[dev]
   ```

5. Checkout your working branch

   ```bash
   git checkout -b your-working-branch
   ```

6. Make your changes

7. Test your changes

   ```bash
   pytest
   flake8 runnable_family tests
   mypy runnable_family tests
   ```

8. Commit your changes

   ```bash
   git add .
   git commit -m "Your commit message"
   ```

9. Push your changes

   ```bash
   git push origin your-working-branch
   ```

10. Create a pull request: [https://github.com/hmasdev/runnable_family/compare](https://github.com/hmasdev/runnable_family/compare)

## License

[MIT](LICENSE)

## Author

[hmasdev](https://github.com/hmasdev)
