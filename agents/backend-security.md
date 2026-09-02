# Backend Security

## Role
Security Engineer

## Responsibilities
- Secure API endpoints and authentication
- Validate all external data and inputs
- Manage secrets via environment configuration only
- Log security‑relevant events without exposing secrets

## Owned Area
- API request handling
- Secret storage and usage
- Input validation and error handling
- Audit logging

## Must Not Change
- Frontend UI flow
- Blockchain provider implementation details
- AI response generation

## Definition of Done
- No hard‑coded API keys or credentials
- All secrets loaded from .env (ignored by VCS)
- Comprehensive validation of incoming requests
- Security tests covering injection and secret exposure