# 🔒 SECURITY POLICY

**Security practices for Kinda chaos engineering platform**

## 🛡️ Reporting Security Vulnerabilities

We take security seriously. If you discover a security vulnerability, please report it responsibly.

### **Security Contact**
- 📧 **Email**: Open a **private** GitHub security advisory
- 🔐 **GitHub**: Use the "Security" tab → "Report a vulnerability"

**DO NOT create public GitHub issues for security vulnerabilities.**

### **Response Timeline**
- **Initial response**: Within 1 week
- **Vulnerability assessment**: Within 2-3 weeks
- **Fix timeline**: Based on severity (1-90 days)
- **Public disclosure**: After fix + coordination

## 🎯 Security Scope

### **In Scope**
- Kinda language interpreter and runtime
- Code transformation and execution pipeline
- File handling and parsing vulnerabilities
- Command injection via malicious .knda files
- Privilege escalation through chaos injection

### **Out of Scope**
- General dependency vulnerabilities (report to upstream)
- Social engineering attacks
- Physical security issues
- DDoS attacks on public infrastructure

## 🔐 Security Features

### **Code Execution Safety**
- **Sandboxed chaos**: Chaos injection isolated from system
- **Input validation**: All .knda files parsed safely
- **No arbitrary execution**: Limited to defined chaos constructs
- **Resource limits**: Prevents resource exhaustion attacks

### **Enterprise Security**
- **Air-gapped deployment**: No network dependencies required
- **Audit logging**: Complete traceability of operations
- **Deterministic execution**: Reproducible with seeds
- **Minimal permissions**: Runs with least required privileges

## 🏢 Enterprise Security

### **Commercial License Security**
- Enhanced security features for production deployment
- Professional security support and incident response
- Custom security configurations for classified environments
- Integration with enterprise security frameworks

### **Defense/Aerospace Security**
- ITAR compliance assistance
- Security clearance support
- Classified system deployment guidance
- Air-gapped operation certification

## 📋 Security Best Practices

### **For Users**
- Always review .knda files before execution
- Use `--seed` for reproducible testing
- Run in isolated environments for untrusted code
- Keep Kinda updated to latest security patches

### **For Developers**
- Follow secure coding practices
- Validate all external inputs
- Use proper error handling
- Regular security testing and review

## 🎯 Security Disclosure

### **Public Disclosure Policy**
- Security fixes released immediately
- CVE assignments for significant vulnerabilities
- Credit given to security researchers
- Coordinated disclosure timeline

### **Security Updates**
- Critical security fixes: Immediate release
- High priority fixes: Within 1 week
- Medium/Low priority: Next scheduled release
- All security updates documented in CHANGELOG

---

## 🤝 Responsible Disclosure

We appreciate security researchers who:
- Report vulnerabilities through proper channels
- Allow reasonable time for fixes
- Don't exploit vulnerabilities maliciously
- Help improve Kinda's overall security

**Thank you for helping keep Kinda secure!** 🛡️