# Releasing

Releases are built and published by `.github/workflows/publish.yml` when a GitHub release is published. The workflow checks the tag against the package version, runs the tests and package checks, then uploads the wheel and source distribution with PyPI provenance attestations.

## One-time PyPI setup

No API token is stored in GitHub. In [PyPI project management](https://pypi.org/manage/projects/), open `sseclient-py`, then **Publishing**, and add a GitHub publisher with these exact values:

- Owner: `mpetazzoni`
- Repository: `sseclient`
- Workflow name: `publish.yml`
- Environment name: `pypi`

Optionally create the `pypi` environment in the GitHub repository settings and require maintainer approval before publishing. If configured on PyPI, the environment name must match.

## Making a release

1. Update `version` in `sseclient/version.py` and merge the release changes to `main`.
2. Create a GitHub release from `main` with tag `sseclient-py-<version>`, for example `sseclient-py-2.0.0`.
3. Publish the GitHub release. The workflow publishes the same version to PyPI and attaches attestations automatically.
4. Check the workflow result and the new PyPI release's **Provenance** section.
