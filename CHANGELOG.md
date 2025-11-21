# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

<!-- insertion marker -->
## [v0.1.11](https://github.com/albertorp/django-strawberry/releases/tag/v0.1.11) - 2025-11-21

<small>[Compare with v0.1.10](https://github.com/albertorp/django-strawberry/compare/v0.1.10...v0.1.11)</small>

## [v0.1.10](https://github.com/albertorp/django-strawberry/releases/tag/v0.1.10) - 2025-11-19

<small>[Compare with v0.1.9](https://github.com/albertorp/django-strawberry/compare/v0.1.9...v0.1.10)</small>

## [v0.1.9](https://github.com/albertorp/django-strawberry/releases/tag/v0.1.9) - 2025-11-19

<small>[Compare with v0.1.8](https://github.com/albertorp/django-strawberry/compare/v0.1.8...v0.1.9)</small>



## [v0.1.8](https://github.com/albertorp/django-strawberry/releases/tag/v0.1.8) - 2025-11-18

<small>[Compare with v0.1.7](https://github.com/albertorp/django-strawberry/compare/v0.1.7...v0.1.8)</small>

## [v0.1.7](https://github.com/albertorp/django-strawberry/releases/tag/v0.1.7) - 2025-11-18

<small>[Compare with v0.1.6](https://github.com/albertorp/django-strawberry/compare/v0.1.6...v0.1.7)</small>

## [v0.1.6](https://github.com/albertorp/django-strawberry/releases/tag/v0.1.6) - 2025-11-18

<small>[Compare with v0.1.5](https://github.com/albertorp/django-strawberry/compare/v0.1.5...v0.1.6)</small>

## [v0.1.5](https://github.com/albertorp/django-strawberry/releases/tag/v0.1.5) - 2025-11-17

<small>[Compare with v0.1.4](https://github.com/albertorp/django-strawberry/compare/v0.1.4...v0.1.5)</small>

## [v0.1.4](https://github.com/albertorp/django-strawberry/releases/tag/v0.1.4) - 2025-11-13

<small>[Compare with v0.1.3](https://github.com/albertorp/django-strawberry/compare/v0.1.3...v0.1.4)</small>

### Removed

- Remove refs to neapolitan in templates ([60f1cd3](https://github.com/albertorp/django-strawberry/commit/60f1cd3abc1999b60b87bea465ff959eea56cda0) by Alberto Rodriguez Prieto).

## [v0.1.3](https://github.com/albertorp/django-strawberry/releases/tag/v0.1.3) - 2025-11-13

<small>[Compare with v0.1.2](https://github.com/albertorp/django-strawberry/compare/v0.1.2...v0.1.3)</small>

## [v0.1.2](https://github.com/albertorp/django-strawberry/releases/tag/v0.1.2) - 2025-11-13

<small>[Compare with v0.1.1](https://github.com/albertorp/django-strawberry/compare/v0.1.1...v0.1.2)</small>

## [v0.1.1](https://github.com/albertorp/django-strawberry/releases/tag/v0.1.1) - 2025-11-13

<small>[Compare with first commit](https://github.com/albertorp/django-strawberry/compare/d7d789333fca1f6251575c2f84ae097b919c1949...v0.1.1)</small>

## Historical Notes (Pre-Conventional Commits, ≤ v0.1.8)

The following summaries describe the project’s evolution before version `0.1.8`, which was the first release created after adopting Conventional Commits. These entries were compiled manually based on development activity and release intent.

---

### v0.1.8 — Internal Improvements (2025-11-18)
- Refined CRUD template structure.
- Improved template loading and fallback rules.
- Adjusted packaging behavior for more consistent template resolution.

### v0.1.7 — Table & View Refinements (2025-11-18)
- Improved table rendering consistency.
- Better integration with `django-tables2`.
- Minor UI/UX consistency fixes and template cleanup.

### v0.1.6 — Template & Actions Column Enhancements (2025-11-18)
- Enhanced actions column template handling.
- Optimized actions template fallback candidate logic.
- Improved resolution order for partial templates used in tables.

### v0.1.5 — CRUD Template Consolidation (2025-11-17)
- Consolidated Strawberry CRUD template names and structure.
- Improved folder layout under `templates/strawberry/`.
- Added initial DaisyUI/Flowbite partials for lists, actions, and modals.

### v0.1.4 — Removed Neapolitan References (2025-11-13)
- Removed direct Neapolitan template references in Strawberry templates.
- Ensured Strawberry uses its own template suite as the default.
- Cleaned up template inheritance to adopt `base_strawberry.html`.

### v0.1.3 — Templates & Packaging Fixes (2025-11-13)
- Added `MANIFEST.in` to include templates and static files in the built package.
- Updated `pyproject.toml` to correctly include package data.
- Ensured proper installation from GitHub/tagged versions.
- Verified Strawberry template overrides load correctly in consuming projects.

### v0.1.2 — Introduced Base Templates & Layout (2025-11-13)
- Added `base_strawberry.html` and `base_minimal.html`.
- Added a full CRUD template suite:
  - list
  - detail
  - form
  - confirm_delete
  - partials (actions, modals, filters, title, top actions)
- Introduced Tailwind/DaisyUI-ready base layout.

### v0.1.1 — Initial Strawberry Templates & CRUD Integration (2025-11-13)
- Added first set of template overrides for Neapolitan CRUD views.
- Introduced Strawberry’s early table and partials templates.
- Integrated DaisyUI/Tailwind-compatible components.

### v0.1.0 — Initial Release (2025-11-13)
- Created project structure (`django-strawberry` and `strawberry/`).
- Added initial `BaseCrudView` extending Neapolitan.
- Included example Django project for local development.
- Established foundation for reusable CRUD operations.
