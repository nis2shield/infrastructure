# Contributing to NIS2 Infrastructure Kit

Thank you for your interest in contributing to NIS2 Infrastructure Kit!

## How to Contribute

### Reporting Issues

- Use GitHub Issues to report bugs or request features
- Include Docker and docker-compose versions
- Provide logs from `docker-compose logs` if applicable

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Test your changes with `docker-compose config`
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

### Areas for Contribution

- **New SIEM outputs**: Loki, Splunk, Datadog configurations
- **Backup strategies**: S3, Azure Blob, MinIO support
- **Security hardening**: Network policies, secrets management
- **Documentation**: Tutorials, video guides, translations

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/infrastructure.git
cd infrastructure

# Copy environment template
cp .env.example .env

# Validate configuration
docker-compose config

# Start in development mode
docker-compose up
```

## Code of Conduct

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.
