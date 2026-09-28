# Release the CLI to PyPI

ModelSpec publishes the `modelspec-dev` distribution. The installed command is
`modelspec`.

## Configure the first release

Jamie must complete these steps once:

1. Create a PyPI account, or log in to the existing account. Enable two-factor
   authentication.
2. Open **Publishing** in PyPI and add a pending Trusted Publisher with these
   values:

   - PyPI project name: `modelspec-dev`
   - Owner: `turbobeest`
   - Repository: `modelspec`
   - Workflow: `release-pypi.yml`
   - Environment: `pypi`

3. In the GitHub repository settings, create an environment named `pypi`.
4. Push the first version tag:

   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

The tag starts `.github/workflows/release-pypi.yml`. The workflow builds the
source distribution and wheel, then authenticates through PyPI Trusted
Publishing. Do not add a PyPI API token to GitHub.

For later releases, update the explicit version in `pyproject.toml`, merge that
change, and push the matching `v*` tag.
