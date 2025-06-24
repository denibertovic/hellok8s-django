# hellok8s-django

A comprehensive Django project template with CI/CD pipeline for deploying to Kubernetes. This project demonstrates modern Python development practices using Nix, devenv, Docker, Helm, and GitHub Actions.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Local Development Setup](#local-development-setup)
- [Running the Application](#running-the-application)
- [Project Structure](#project-structure)
- [CI/CD Pipeline](#cicd-pipeline)
- [Deployment](#deployment)
- [Secrets Management](#secrets-management)
- [Using as a Template](#using-as-a-template)
- [GitHub Secrets Configuration](#github-secrets-configuration)

## Prerequisites

Before you begin, you'll need to install several tools to work with this project effectively.

### 1. Install Nix

First, you need to install Nix, a powerful package manager that ensures reproducible development environments.

**For macOS users** (and others who want the best experience), we strongly recommend using the Determinate Systems Nix installer:

```bash
curl --proto '=https' --tlsv1.2 -sSf -L https://install.determinate.systems/nix | sh -s -- install
```

This installer provides better defaults and improved user experience compared to the official installer. For more details, visit: https://docs.determinate.systems/determinate-nix/

**If you want**, you can use the official installer (but you'll probably need to manually enable nix flakes):

```bash
sh <(curl -L https://nixos.org/nix/install) --daemon
```

After installation, restart your terminal or source your shell profile.

### 2. Install devenv

[devenv](https://devenv.sh) is a tool that creates reproducible development environments using Nix. Install it with:

```bash
nix profile install --accept-flake-config github:cachix/devenv/latest
```

### 3. Install direnv

[direnv](https://direnv.net/) automatically loads environment variables when you enter a directory. This integrates perfectly with devenv.

**On macOS:**

```bash
brew install direnv
```

**On Linux:**

```bash
nix profile install nixpkgs#direnv
```

**Shell Integration:**
Add the following to your shell configuration file (`~/.bashrc`, `~/.zshrc`, etc.):

```bash
eval "$(direnv hook bash)"  # for bash
eval "$(direnv hook zsh)"   # for zsh
```

Restart your terminal after adding the hook.

## Local Development Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/denibertovic/hellok8s-django.git
   cd hellok8s-django
   ```

2. **Allow direnv to manage the environment:**

   ```bash
   direnv allow
   ```

   This command tells direnv that you trust this directory to automatically load environment variables. You'll be prompted to do this the first time you enter the directory.

3. **Enter the development shell:**
   Once direnv is allowed, it will automatically activate the devenv shell whenever you're in the project directory. You'll see your prompt change, indicating you're in the development environment with all necessary tools available.

4. **Configure environment variables:**
   Copy the example environment file and fill in the required values:

   ```bash
   cp env.example .env
   ```

   Open `.env` in your editor and fill in the necessary configuration values. The example file contains all the environment variables needed for local development with sensible defaults. You'll need to set values for:

   - Database connection settings
   - Django secret key
   - Any API keys or external service configurations

   **Note:** The `.env` file is automatically loaded by direnv when you're in the project directory.

## Running the Application

### Start All Services

To bring up all required services (PostgreSQL, Django, Tailwind, etc.) in the background:

```bash
devenv up
```

This command starts all the services defined in `devenv.nix` using process-compose. The services will run in the background and restart automatically if they crash.

### Run Database Migrations

Like any Django project, you need to set up the database:

```bash
./manage.py migrate
```

### Access the Application

Visit http://localhost:8000 in your browser to see your Django application running!

### Create a Superuser (Optional)

To access the Django admin interface:

```bash
./manage.py createsuperuser
```

Then visit http://localhost:8000/admin/ to log in.

## Project Structure

This Django project is organized into several apps:

- **`myauth/`** - Custom user model
- **`post/`** - Just simple blog post functionality
- **`myutils/`** - Shared utilities and abstract model behaviors
- **`core/`** - Core functionality including custom storage classes
- **`project/`** - Django project settings and configuration
- **`chart/`** - Helm chart for Kubernetes deployment

### Key Technologies

- **Django 5.2+** - Web framework
- **PostgreSQL** - Database (configured via devenv)
- **uv** - Fast Python package manager (replaces pip/poetry)
- **Tailwind CSS** - Utility-first CSS framework
- **Docker** - Containerization
- **Kubernetes + Helm** - Orchestration and deployment
- **GitHub Actions** - CI/CD pipeline

## CI/CD Pipeline

This project uses GitHub Actions with a reusable workflow architecture that supports deploying to multiple environments (staging, production, etc.).

### How It Works

1. **Triggering Builds:**

   - Every push to `main` triggers the CI pipeline
   - Pull requests run tests and build validation
   - Tags trigger production deployments

2. **Docker Image Building:**
   The application is packaged into a Docker container but it uses `uv` for fast, reproducible builds of it's dependencies:

   ```dockerfile
   # Uses uv for lightning-fast dependency installation
   FROM python:3.13-slim
   COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
   # ... rest of Dockerfile
   ```

3. **Reusable Workflow:**
   The `.github/workflows/` directory contains reusable workflow templates that can be called from different environments:

   ```yaml
   # Example: Deploy to prod
   jobs:
     deploy:
       uses: ./.github/workflows/deploy.yml
       with:
         environment: prod
         namespace: hellok8s
   ```

## Deployment

### Helm Chart Structure

The Kubernetes deployment uses Helm for templating and configuration management:

```
chart/
├── Chart.yaml          # Chart metadata
├── values.yaml         # Default values
├── templates/
│   ├── deployment.yaml # Django app deployment
│   ├── service.yaml    # Kubernetes service
│   ├── ingress.yaml    # Ingress configuration
└── values/
    └── prod.yaml # Production-specific values
```

### Deployment Process

1. **GitHub Actions builds and pushes Docker image to docker hub**
2. **Helm chart is deployed to Kubernetes cluster**
3. **SOPS decrypts environment-specific secrets during deployment**
4. **Rolling deployment ensures zero-downtime updates**

The deployment command looks like:

```bash
make IMAGE_TAG=sha-123 ENVIRONMENT=prod NAMESPACE=hellok8s KUBECONFIG=/path/to/kubeconfig.yaml deploy
```

## Secrets Management

This project uses [SOPS](https://github.com/mozilla/sops) for managing encrypted secrets in the repository.

### How SOPS Works Here

1. **Environment Variables:** Database passwords, API keys, and other secrets are stored encrypted in `chart/values/<env>/secrets.yaml`
2. **Encryption:** We use **age** encryption (though AWS KMS and other are also supported)
3. **CI/CD Integration:** GitHub Actions runners decrypt secrets during deployment using the private age key
4. **Runtime:** Secrets are injected into Kubernetes pods as environment variables

### SOPS Configuration

The `.sops.yaml` file defines encryption rules:

```yaml
creation_rules:
  - path_regex: \.yaml$
    age: age1... # public age key
```

### Alternative: AWS KMS

For production systems, consider using AWS KMS instead of age keys. See the [SOPS documentation](https://github.com/getsops/sops?tab=readme-ov-file#using-sops-yaml-conf-to-select-kms-pgp-and-age-for-new-files) for configuration details.

## Using as a Template

Want to use this project as a starting point for your own Django application? Here's how:

### 1. Clone and Reset Git History

```bash
# Clone the repository
git clone https://github.com/denibertovic/hellok8s-django.git my-new-project
cd my-new-project

# Remove the existing git history
rm -rf .git

# Initialize a new git repository
git init
git add .
git commit -m "Initial commit from hellok8s-django template"

# Add your own remote origin
git remote add origin https://github.com/yourusername/my-new-project.git
git push -u origin main
```

### 2. Customize the Project

- Update `pyproject.toml` with your project name and details
- Modify Django settings in `project/settings.py`
- Update the Helm chart in `chart/` with your application name
- Customize the README.md for your project

### 3. Set Up Your Development Environment

Follow the [Local Development Setup](#local-development-setup) instructions above.

## GitHub Secrets Configuration

To enable the CI/CD pipeline, you need to configure several secrets in your GitHub repository.

### Repository Secrets

These secrets are available to all environments and workflows:

1. **`DOCKERHUB_USERNAME`** - Your Docker Hub username

   ```
   example: johndoe
   ```

2. **`DOCKERHUB_TOKEN`** - Your Docker Hub access token

   ```
   Generate at: https://hub.docker.com/settings/security
   ```

3. **`AGE_KEY_FILE`** - Private age key for SOPS decryption

   **Generate an age key:**

   ```bash
   # Install age if you haven't already
   nix profile install nixpkgs#age

   # Generate a new key pair
   age-keygen -o age-key.txt

   # Copy the ENTIRE contents of age-key.txt as the secret value
   cat age-key.txt
   ```

   **Alternative: AWS KMS**
   Instead of age keys, you can use AWS KMS for encryption. See the [SOPS documentation](https://github.com/getsops/sops?tab=readme-ov-file#using-sops-yaml-conf-to-select-kms-pgp-and-age-for-new-files) for setup instructions.

### Environment Secrets

Create a **production** environment in your repository settings, then add:

4. **`KUBECONFIG_YAML`** - Your Kubernetes cluster configuration

   **⚠️ Important:** This should be an **Environment Secret**, not a Repository Secret, for better security isolation.

   ```bash
   # Get your kubeconfig content
   cat ~/.kube/config
   # Copy the entire YAML content as the secret value
   ```

### Setting Up Secrets in GitHub

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Add the three repository secrets listed above
4. Click **Environments** → **New environment** → Name it "production"
5. Add the `KUBECONFIG_YAML` secret to the production environment

### Alternative Container Registries

If you prefer to use AWS ECR, Google Container Registry, or another registry instead of Docker Hub:

1. Replace `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` with appropriate credentials
2. Update the Docker registry configuration in `.github/workflows/` files
3. Update the Helm chart's image repository settings in `chart/values.yaml`

---

## License

This project is open source and available under the [BSD 3-Clause License](LICENSE).
