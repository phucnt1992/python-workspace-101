# 🐍 Python workspace 101 for starters

This repository is a simple Python workspace setup for beginners.
It includes a basic project structure, a virtual environment, and instructions to get started with Python development.

## ✅ What's included

- **uv**: A tool to manage Python versions and virtual environments.
- **node.js lts**: For running linting tools like markdownlint-cli2.
- **pre-commit**: A framework for managing and maintaining multi-language pre-commit hooks.
- **black**: A code formatter for Python.
- **isort**: A Python utility for sorting imports.
- **flake8**: A tool for style guide enforcement.
- **pytest**: A testing framework for Python.

## 💻 Getting Started

- Install Node.js LTS version the [instructions](https://nodejs.org/en/download)

- Install uv tool by following the [instructions](https://docs.astral.sh/uv/getting-started/installation/).

- Install Python 3.12 or higher by following command:

  ```bash
  uv python install --default 3.12
  ```

- Verify the installation by checking the Python version:

  ```bash
  python --version

  # Output should be: Python 3.12.x
  ```

- Sync the dependencies:

  ```bash
  uv sync
  ```

- Run the application:

  ```bash
  uv run main.py

  # Output should be: Hello, World!
  ```

- Install pre-commit to setup git hooks:

  ```bash
  uv run pre-commit install
  ```

- Run pre-commit checks manually after committing changes:

  ```bash
  uv run pre-commit run --all-files
  ```

## 👋 Contributing

Feel free to fork this repository and make improvements. Pull requests are welcome!

Happy coding! 🚀
