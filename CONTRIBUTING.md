# Contributing to Linux Server Admin Bot

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

Be respectful and inclusive. We welcome contributions from everyone.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/artcc/linux-server-admin-bot/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, Docker version)
   - Logs or screenshots if applicable

### Suggesting Features

1. Check if the feature has been suggested in [Issues](https://github.com/artcc/linux-server-admin-bot/issues)
2. Create a new issue with:
   - Clear use case
   - Proposed implementation (if you have ideas)
   - Why this feature would be useful

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the coding standards (see below)
   - Add tests for new functionality
   - Update documentation if needed

4. **Test your changes**
   ```bash
   pytest
   black .
   ruff check .
   mypy bot/ config/
   ```

5. **Commit your changes**
   ```bash
   git commit -m "feat: add amazing new feature"
   ```
   Follow [Conventional Commits](https://www.conventionalcommits.org/)

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Provide a clear description of changes
   - Reference any related issues
   - Ensure all checks pass

## Development Setup

```bash
# Clone your fork
git clone https://github.com/artcc/linux-server-admin-bot.git
cd linux-server-admin-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your values

# Run tests
pytest

# Run the bot locally
python main.py
```

## Coding Standards

### Python Style
- Follow PEP 8
- Use type hints for all functions
- Maximum line length: 100 characters
- Use docstrings for all public functions/classes

### Formatting
- Use `black` for code formatting
- Use `ruff` for linting
- Use `mypy` for type checking

### Naming Conventions
- Classes: `PascalCase`
- Functions/Variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private methods: `_leading_underscore`

### Documentation
- All public APIs must have docstrings
- Use Google-style docstrings
- Update README.md for user-facing changes

### Testing
- Write tests for all new features
- Maintain or improve code coverage
- Use pytest fixtures for reusable components

## Project Structure

```
bot/
├── handlers/    # Telegram command handlers
├── services/    # Business logic
├── monitors/    # Background tasks
├── models/      # Data models
└── utils/       # Utilities

config/          # Configuration management
tests/           # Unit and integration tests
docs/            # Additional documentation
```

## Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(monitor): add network bandwidth monitoring
fix(alerts): prevent duplicate alert notifications
docs(readme): update installation instructions
```

## Questions?

Feel free to open an issue with your question or reach out to the maintainers.

Thank you for contributing! 🎉
