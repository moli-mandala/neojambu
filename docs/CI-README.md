# 🚀 GitHub CI/CD Pipeline

Comprehensive GitHub Actions setup for the NeoJambu linguistics webapp with performance testing, security scanning, and automated deployment.

## 📋 Pipeline Overview

### 🔄 Main CI Pipeline (`.github/workflows/ci.yml`)
**Triggers:** Push to `main`/`develop`, PRs to `main`, weekly schedule

**Jobs:**
- **Test Suite** - Python 3.10, 3.11, 3.12 matrix
- **Code Quality** - Ruff, Black, isort, MyPy
- **Security Scan** - Bandit, Safety dependency check
- **Performance Benchmarks** - Database query timing, Flask response times
- **Deployment Test** - Simulated Heroku deployment
- **Test Report** - Consolidated results summary

### 🔍 Pull Request Pipeline (`.github/workflows/pr.yml`)
**Triggers:** Pull requests to `main`

**Features:**
- **Change Detection** - Only runs relevant tests for changed files
- **Quick Tests** - Fast syntax and import validation
- **Conditional Testing** - Database tests only when needed
- **Security Validation** - Automated security scanning
- **Deployment Checks** - Validates Heroku configuration files

### 🎉 Release Pipeline (`.github/workflows/release.yml`)
**Triggers:** Git tags starting with `v*`

**Features:**
- **Full Test Suite** - Complete validation before release
- **Automated Changelog** - Performance metrics and feature summary
- **GitHub Release** - Creates release with deploy button
- **Heroku Deployment** - Automatic deployment (if configured)

## 🛠️ Development Tools

### Code Quality
```bash
# Linting
uv run ruff check .

# Formatting  
uv run black .

# Import sorting
uv run isort .

# Type checking
uv run mypy .
```

### Security
```bash
# Security scan
uv run bandit -r .

# Dependency vulnerabilities
uv run safety check
```

### Testing
```bash
# Run all tests
uv run pytest test_webapp.py -v

# Performance tests
uv run python test_performance.py

# Deployment verification
uv run python verify_deployment.py

# CI setup validation
uv run python test_ci_setup.py
```

## 📊 Performance Monitoring

The CI pipeline automatically benchmarks:
- **Database queries** with 313k lemmas
- **Index performance** (should be <100ms)
- **Flask route response times** (should be <2s)
- **Session management** efficiency

### Performance Thresholds
```python
thresholds = {
    'reflex_count_query': 0.1,    # < 100ms with index
    'ordered_query': 0.05,        # < 50ms with index  
    'session_query': 0.1,         # < 100ms
    'route_entries': 2.0,         # < 2s
    'route_languages': 1.0,       # < 1s
}
```

## 🔐 Security Scanning

### Bandit - Static Security Analysis
- Scans for common security issues
- Checks for hardcoded passwords, SQL injection risks
- Reports saved as artifacts

### Safety - Dependency Vulnerability Check
- Scans for known vulnerabilities in dependencies
- Checks against safety database
- Reports saved as artifacts

## 🎯 Badge Status

Add these badges to your README:

```markdown
![CI](https://github.com/your-username/neojambu/workflows/CI/badge.svg)
![Security](https://github.com/your-username/neojambu/workflows/Security/badge.svg)
![Deploy](https://github.com/your-username/neojambu/workflows/Deploy/badge.svg)
```

## ⚙️ GitHub Secrets Configuration

For automated Heroku deployment, configure these secrets:

```
HEROKU_API_KEY     - Your Heroku API key
HEROKU_APP_NAME    - Your Heroku app name  
HEROKU_EMAIL       - Your Heroku account email
```

## 🚀 Quick Start

1. **Push code** to trigger CI
2. **Create PR** for change validation
3. **Tag release** with `git tag v1.0.0 && git push --tags`
4. **Monitor** pipeline in GitHub Actions tab

## 📁 CI Configuration Files

- `.github/workflows/ci.yml` - Main CI/CD pipeline
- `.github/workflows/pr.yml` - Pull request validation
- `.github/workflows/release.yml` - Release automation
- `pyproject.toml` - Tool configuration (ruff, black, etc.)
- `test_ci_setup.py` - Local CI validation
- `verify_deployment.py` - Deployment health checks

## 🔧 Troubleshooting

### Common Issues

**uv not found:**
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Dependencies not installing:**
```bash
# Clear cache and reinstall
uv cache clean
uv sync --reinstall
```

**Tests failing locally:**
```bash
# Run CI setup test
uv run python test_ci_setup.py

# Check specific tool
uv run ruff check .
```

**Performance tests failing:**
```bash
# Download database first
curl -L https://github.com/moli-mandala/data/releases/latest/download/data.db -o data.db

# Create indexes
uv run python -c "
from sqlalchemy import create_engine, text
engine = create_engine('sqlite:///data.db')
with engine.connect() as conn:
    conn.execute(text('CREATE INDEX IF NOT EXISTS idx_lemmas_origin_lemma_id ON lemmas(origin_lemma_id)'))
    # ... other indexes
"
```

## 🎉 Benefits

✅ **Automated Testing** - Catches issues before production  
✅ **Performance Monitoring** - Ensures 313k lemma database stays fast  
✅ **Security Scanning** - Identifies vulnerabilities early  
✅ **Multi-Python Support** - Tests across Python 3.10-3.12  
✅ **Fast Builds** - uv provides 10-100x faster installs  
✅ **Quality Gates** - Code quality checks on every change  
✅ **Deployment Validation** - Tests Heroku configuration  
✅ **Automated Releases** - One-click deployment to production

---

**Questions?** Check the [GitHub Actions documentation](https://docs.github.com/en/actions) or review the workflow files in `.github/workflows/`.