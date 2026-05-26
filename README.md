# 🐍 python-workspace-101

A simple Python monorepo workspace setup demonstrating modern Python development practices with multi-package organization,
FastAPI REST API, CLI tools, and browser-based E2E testing.

## 📋 Table of Contents

- 📖 [About](#-about)
- ✨ [Features](#-features)
- 📋 [Prerequisites](#-prerequisites)
- 🚀 [Installation](#-installation)
- ⚡ [Quick Start](#-quick-start)
- 💻 [Development](#-development)
- 🧪 [Testing](#-testing)
- 🔄 [CI/CD](#-cicd)
- 🤝 [Contributing](#-contributing)
- 📄 [License](#-license)

## 📖 About

**python-workspace-101** is a starter template for Python developers learning how to set up a professional workspace
with modern tooling.It demonstrates workspace structure, task automation, testing patterns,
and continuous integration best practices using industry-standard tools.

## ✨ Features

- 📦 **Monorepo Workspace** — Organized packages for domain, infrastructure, use cases, CLI, and REST API
- 🔌 **FastAPI REST API** — Async HTTP server with PostgreSQL integration and OpenAPI documentation
- 💻 **CLI Tool** — Command-line interface for workspace interactions
- 🎨 **Web UI** — HTMX-based Todo web interface
- 🧪 **Comprehensive Testing** — Unit tests, integration tests, and browser-based E2E tests with Playwright
- 🔍 **Code Quality** — Ruff linting and formatting, pre-commit hooks
- ⚙️ **Task Automation** — Taskfile-based command standardization
- 🔄 **CI/CD Ready** — GitHub Actions workflow for automated testing and linting

## 📋 Prerequisites

Before you start, ensure you have the following installed:

- 🐍 **Python 3.13+** — [Download](https://www.python.org/downloads/)
- 📦 **uv** — Python package manager and environment tool — [Installation Guide](https://docs.astral.sh/uv/getting-started/installation/)
- 📘 **Node.js LTS** — Required for markdown linting tools — [Download](https://nodejs.org/en/download)
- ✅ **Taskfile** — Task runner for standardized commands — [Installation Guide](https://taskfile.dev/#/installation)

## 🚀 Installation

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/phucnt1992/python-workspace-101.git
cd python-workspace-101
```

### 2️⃣ Initialize the Workspace

Initialize your environment by installing Python, creating a virtual environment, and syncing dependencies:

```bash
task init
```

This command:

- 🐍 Installs Python 3.13
- 🔧 Creates a virtual environment
- 📚 Syncs all project dependencies
- 🪝 Installs git pre-commit hooks
- 🎭 Installs Playwright for browser testing

### 3️⃣ Verify Installation

Run the linter to verify your setup:

```bash
task lint
```

## ⚡ Quick Start

### 🔌 Run the REST API Server

Start the FastAPI server (requires a PostgreSQL database):

```bash
APP_DB_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/todos task app
```

Once running, access:

- 📚 **Swagger UI API Docs** — <http://localhost:8000/docs>
- 📄 **OpenAPI JSON** — <http://localhost:8000/openapi.json>
- 📝 **Todo Web UI** — <http://localhost:8000/ui/todos>

### 💻 Run the CLI

Execute CLI commands:

```bash
task cli [arguments]
```

### 🔄 Sync Dependencies

When dependencies change, re-sync your environment:

```bash
task sync
```

## 💻 Development

### 🎨 Format Code

Format all Python code with Ruff:

```bash
task fmt
```

### 🔍 Run Linter

Check code quality with Ruff:

```bash
task lint
```

### 🪝 Run Pre-commit Hooks

Manually run all pre-commit hooks (also runs automatically on commit):

```bash
task pre-commit
```

## 🧪 Testing

### ▶️ Run All Tests

Run unit tests, integration tests, and E2E tests:

```bash
task test
```

### 🎯 Run Specific Test Suites

- 🖥️ **CLI Tests:** `task test-cli`
- 🔌 **API Tests:** `task test-api`
- 🎭 **Browser E2E Tests:** `task test-e2e`

### 📊 Generate Coverage Report

Run tests and generate a detailed coverage report:

```bash
task test-cov
```

## 🔄 CI/CD

This repository uses GitHub Actions for continuous integration.

### ⚙️ Workflow Details

- 🎯 **Trigger:** Pull requests targeting the `main` branch
- 📋 **Steps:**
  1. ✅ Run code quality checks (`task lint`)
  2. 🧪 Run all tests (`task test`)
- 📊 **Coverage:** Test coverage is reported in the output but is not enforced as a required gate
- 🔒 **Required Check:** `CI / ci` must pass before merging

### 🏃 Running CI Locally

To test the CI pipeline locally:

```bash
task ci
```

This runs both linting and testing, matching the CI workflow.

## 🤝 Contributing

Contributions are welcome! To contribute:

1. 🍴 **Fork** the repository
2. 🌿 **Create a feature branch:** `git checkout -b feature/your-feature`
3. ✏️ **Make your changes** and commit with clear messages
4. 🧪 **Run tests locally:** `task test`
5. 🔍 **Run linting:** `task lint`
6. 📤 **Submit a pull request** targeting the `main` branch

All pull requests must pass the CI workflow (`task ci`) before merging.

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

🎉 **Happy coding! 🚀**
