# Releasing SimWork

This project releases from `main` using Semantic Versioning and an annotated git tag.

## Release principles

- Release only from a green `main` branch.
- Update `CHANGELOG.md` in the same commit as the release-ready code or release metadata.
- Add versioned release notes under `docs/releases/` for each public release.
- Keep deployment health checks aligned with real application endpoints.
- Tag the exact commit that is deployed.

## Release checklist

1. Ensure the `main` branch contains the intended production changes.
2. Confirm CI is green for the release commit.
3. Update versions in application metadata if the release version changes.
4. Add a new entry to `CHANGELOG.md`.
5. Add release notes in `docs/releases/<version>.md`.
6. Run local verification:
   - Backend: `uv run ruff check .` and `uv run pytest tests/ -v`
   - Frontend: `npm run lint` and `npm run build`
7. Merge or push the release-preparation commit to `main`.
8. Create an annotated tag, for example `git tag -a v1.0.0 -m "v1.0.0"`.
9. Push `main` and the tag.
10. Publish release notes in GitHub Releases using the matching `docs/releases/<version>.md` content.
11. Verify production deployments:
   - Vercel deployment succeeds for `main`
   - Railway deployment succeeds for `main`
   - Backend health endpoint returns `200 OK`
12. Run a smoke test on the deployed frontend and backend.

## Ongoing maintenance

- Keep an `Unreleased` section at the top of `CHANGELOG.md` between releases.
- Group changelog entries under `Added`, `Changed`, `Fixed`, `Removed`, and `Security` where useful.
- Write release notes for users and operators; write the changelog as the durable engineering record.
- Keep tracked documentation minimal: shared project docs at repo root, release notes under `docs/releases/`, and local working materials under `.local/docs/`.
