# 🐍 Python workspace 101 for starters

This repository is a simple Python workspace setup for beginners.
It includes a basic project structure, a virtual environment, and instructions to get started with Python development.

## ✅ What's included

- **Taskfile**: A task runner to standardize local developer commands.
- **uv**: Used under the hood by Taskfile tasks for Python environment and dependency management.
- **node.js lts**: For running linting tools like markdownlint-cli2.

## 💻 Getting Started

- Install Node.js LTS version the [instructions](https://nodejs.org/en/download)

- Install uv tool by following the [instructions](https://docs.astral.sh/uv/getting-started/installation/).

- Install Taskfile by following the [instructions](https://taskfile.dev/#/installation).

- Initialize the workspace (create venv + sync dependencies):

  ```bash
  task init
  ```

- Re-sync dependencies when needed:

  ```bash
  task sync
  ```

- Run lint checks:

  ```bash
  task lint
  ```

- Run tests:

  ```bash
  task test
  ```

- Run pre-commit checks manually:

  ```bash
  task pre-commit
  ```

## 🔄 Pull Request CI

- Pull requests targeting `main` run GitHub Actions workflow `CI`.
- The workflow executes `task ci`, which runs:
  - `task lint`
  - `task test`
- Coverage is reported as part of test output and is not used as a required threshold gate.
- Recommended required status check for branch protection: `CI / ci`.

## Appendix

## 👋 Contributing

Feel free to fork this repository and make improvements. Pull requests are welcome!

Happy coding! 🚀
