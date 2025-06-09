# Contributing to Resume Velvit Thunder

Thank you for your interest in contributing to Resume Velvit Thunder! We welcome contributions from everyone, regardless of experience level. This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Your First Code Contribution](#your-first-code-contribution)
  - [Pull Requests](#pull-requests)
- [Development Workflow](#development-workflow)
- [Coding Guidelines](#coding-guidelines)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Code Review Process](#code-review-process)
- [Community](#community)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to [contact@resume-velvit-thunder.com](mailto:contact@resume-velvit-thunder.com).

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
   ```bash
   git clone https://github.com/yourusername/resume-velvit-thunder.git
   cd resume-velvit-thunder
   ```
3. **Set up the development environment** (see [Development Guide](/docs/development/README.md))
4. **Create a branch** for your changes
   ```bash
   git checkout -b feature/your-feature-name
   ```

## How to Contribute

### Reporting Bugs

Bugs are tracked as [GitHub issues](https://github.com/yourusername/resume-velvit-thunder/issues). Before creating a new issue:

1. **Check if the issue has already been reported**
2. **Use a clear and descriptive title**
3. **Include as much information as possible**:
   - Steps to reproduce the issue
   - Expected vs. actual behavior
   - Screenshots if applicable
   - Browser/OS version if relevant
   - Any error messages

### Suggesting Enhancements

We welcome suggestions for new features and improvements. When suggesting an enhancement:

1. **Check if the enhancement has already been suggested**
2. **Clearly describe the enhancement**
3. **Explain why this enhancement would be useful**
4. **Provide examples of how it would be used**

### Your First Code Contribution

Looking for your first contribution? Here are some good places to start:

- Issues labeled `good first issue`
- Fixing typos in documentation
- Adding test cases
- Improving error messages

### Pull Requests

1. **Keep your PRs small and focused**
2. **Update documentation** as needed
3. **Add tests** for new functionality
4. **Run all tests** before submitting
5. **Reference related issues** in your PR description
6. **Follow the PR template**

## Development Workflow

1. **Create a branch** for your feature/fix
2. **Make your changes**
3. **Run tests** locally
4. **Commit your changes** following the commit message guidelines
5. **Push to your fork**
6. **Open a Pull Request**

## Coding Guidelines

### Python

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints for all new code
- Write docstrings following [Google style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- Keep functions small and focused

### JavaScript/TypeScript

- Follow [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- Use TypeScript for all new code
- Write JSDoc comments for all public functions
- Prefer functional components with hooks

### Testing

- Write tests for all new functionality
- Follow the Arrange-Act-Assert pattern
- Keep tests independent and isolated
- Test edge cases and error conditions

## Commit Message Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types

- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools

### Examples

```
feat(auth): add password reset functionality

- Add password reset endpoint
- Send password reset email
- Update documentation

Closes #123
```

## Code Review Process

1. **Initial Review**
   - A maintainer will review your PR
   - They may request changes or ask questions

2. **Addressing Feedback**
   - Make the requested changes
   - Push your updates
   - Comment on the PR when ready for re-review

3. **Approval**
   - Once approved, a maintainer will merge your PR
   - Your contribution will be included in the next release

## Community

- **Discord**: [Join our Discord server](https://discord.gg/your-invite)
- **Twitter**: [Follow us on Twitter](https://twitter.com/yourhandle)
- **Blog**: [Read our blog](https://blog.resume-velvit-thunder.com)

## Thank You!

Your contributions help make Resume Velvit Thunder better for everyone. Thank you for being part of our community!
