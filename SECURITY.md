# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to: **security@nis2shield.com**

Please include:
- Type of issue (e.g., container escape, credential exposure, etc.)
- Docker/docker-compose version
- Step-by-step instructions to reproduce
- Impact assessment

## Security Best Practices for Deployment

1. **Never commit `.env` files** - Use `.env.example` as template
2. **Rotate secrets regularly** - Database passwords, API tokens
3. **Use Docker secrets** in production instead of environment variables
4. **Keep images updated** - Regularly pull latest base images
5. **Enable TLS** for all SIEM connections
6. **Restrict network access** - Use Docker networks to isolate services
