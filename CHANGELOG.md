# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog and this project uses Semantic Versioning.

## [Unreleased]

- No unreleased changes yet.

## [1.0.0] - 2026-03-17

### Added
- PR CI workflow for backend Ruff and pytest plus frontend lint and production build.
- Frontend environment example for Vercel and local setup.
- Release process documentation and versioned release notes.

### Changed
- Promoted the current authentication, UI, agent-routing, and scenario work to the first production release.
- Updated frontend and backend application metadata to version `1.0.0`.
- Aligned Railway health checks with the live backend health endpoint.
- Reduced tracked project documentation to the current shared surface: root docs plus versioned release notes.

### Fixed
- Removed legacy frontend and backend files that were surviving the `develop` to `main` merge and breaking CI.
- Resolved frontend workspace lint and build blockers in the current app-router implementation.
- Removed stale PRD-era and reference files from tracked `docs/` in favor of ignored local-only documentation.
