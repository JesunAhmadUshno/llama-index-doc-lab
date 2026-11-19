# Changelog

All notable changes to this project. Format: Keep a Changelog 1.1.
Versions follow Semantic Versioning; no release is tagged yet.

## [Unreleased]

### Changed
- 2026-11-08: Adopted the portfolio standard v2. README opens with the
  question, headline, field, job family and verdict (Functional), then
  reproduce commands, lifecycle and a layout table mapping the locked
  names to their roles. AUDIT.md is the report; its grade moved out of
  the public repo (grades are internal) and every limitation it listed
  is kept under Threats to validity. A test pins the SHA-256 of
  PREREGISTRATION.md as committed in 9534f68 (tag proposal-v1). CI
  runs with read-only permissions and checks that RESULTS.md and
  results/ regenerate unchanged from results/raw_runs.json. CodeQL and
  Dependabot added. The paid Jev claim_check step left the reproduce
  path.

### Added
- 2026-11-08: Results (4dc544a): H1 REFUTED, H2 CONFIRMED, H3 REFUTED,
  with the audit and the Jev claim_check record.
- 2026-11-08: Harness (9234c43): both arms, frozen question set,
  metrics, tests and CI.
- 2026-11-08: Pre-registration (9534f68), before any code or result.
