# Contributing to Kinda

Thanks for your interest in contributing to the Kinda Language project! We welcome issues, PRs, docs, and chaos suggestions.

---

## 🧩 How to Contribute

### 🐛 Report Bugs
Open a GitHub issue with:

- A clear, reproducible example
- Expected vs. actual behavior
- Your OS and Python version (if relevant)

### ✨ Suggest Features
We love weird ideas. Open an issue or discussion with:

- What the feature does
- Why it fits Kinda's fuzzy vibe
- Any syntax ideas or example code

### 🧪 Add Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=kinda --cov-report=term-missing
```

Add tests in `tests/python/` alongside the transformer or runtime behavior you're validating.

### 🔧 Submit Code

1. Fork the repo
2. Create a branch (`git checkout -b feature/my-awesome-idea`)
3. Write tests and docs
4. Commit and push
5. Open a PR

CI will run on all PRs targeting `main`.

---

## 🧠 Project Philosophy

- **Inject chaos**, not confusion
- Be **portable**, **fun**, and **pluggable**
- Stay **respectful** of tooling (CI, IDEs)
- **Document weirdness** – if it’s not obvious, write it down

---

## 🧹 Code Style

We don’t lint yet, but try to:

- Follow [PEP8](https://peps.python.org/pep-0008/)
- Keep functions small and readable
- Comment Kinda logic clearly

---

## 📚 Docs

Docs live in `/docs`. PRs welcome to clarify, expand, or explain new behavior.

---

## 📦 Dependencies

We try to minimize them. If you need one, make sure it’s:

- Actively maintained
- MIT-compatible
- Installable via `pip install`

---

## 🤝 Code of Conduct

Be kind. Be weird, but not rude. We're building a community where nerdy humor and inclusive collaboration can thrive.

---

Thanks for helping build Kinda. Now go break something... kinda.
