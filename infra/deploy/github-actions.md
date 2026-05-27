# GitHub Actions Deployment

## Overview

Memory Distiller uses two GitHub Actions workflows:

- **CI** (`.github/workflows/ci.yml`): Runs on every PR and push to main. Runs tests, Ruff, Ruff format check, and mypy.
- **Deploy** (`.github/workflows/deploy.yml`): Runs on every push to main and can be triggered manually via `workflow_dispatch`. First runs CI steps, then deploys to the VPS.

## Required GitHub Secrets

The Deploy workflow requires these secrets to be configured in the repository:

- `VPS_HOST`
- `VPS_USER`
- `VPS_PORT`
- `VPS_SSH_KEY`

## How to Rotate Deploy Key

1. On the VPS, generate a new SSH key pair for the deploy user:
   ```bash
   ssh-keygen -t ed25519 -f ~/.ssh/deploy_key
   ```
2. Add the public key to the `memory-deploy` user's `authorized_keys`:
   ```bash
   cat ~/.ssh/deploy_key.pub >> ~/.ssh/authorized_keys
   ```
3. Copy the private key content.
4. In the GitHub repository, go to **Settings → Secrets and variables → Actions**.
5. Update the `VPS_SSH_KEY` secret with the new private key content.

## How the Deploy User Works

The `memory-deploy` user is a low-privilege user on the VPS. It is configured in sudoers to allow running only one specific deployment script via `sudo`:

```
memory-deploy ALL=(ALL) NOPASSWD: /usr/local/bin/deploy-memory-distiller
```

This means the GitHub Actions deploy step can only trigger that exact script and nothing else on the server.

## Manual Deployment Trigger

To trigger a deployment manually:

```bash
gh workflow run deploy.yml
```

## Inspect Runs

List recent workflow runs:

```bash
gh run list
```

View details of a specific run:

```bash
gh run view <run-id>
```

## Security Notes

- **No root SSH from GitHub Actions**: The deploy user cannot write to system directories or escalate privileges beyond the single allowed script.
- **No Basic Auth password in Actions**: Authentication is handled via SSH key only.
- **No DEEPSEEK_API_KEY in Actions**: The API key is not stored in GitHub Secrets and is never exposed to the CI/deploy workflows. It stays resident on the VPS and is sourced from the server's own `.env` file.
- **Server .env stays on VPS**: Environment variables (including any secrets) are managed on the VPS itself and are not part of the GitHub Actions workflow.
- **Deploy user restricted to one script**: The sudoers configuration ensures the deploy user cannot run arbitrary commands on the VPS.
