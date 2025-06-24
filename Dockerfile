#syntax=docker/dockerfile:1.4
FROM python:3.13-slim

# install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1
ENV UV_NO_MANAGED_PYTHON=1
ENV UV_PYTHON_DOWNLOADS=never

RUN mkdir /app
WORKDIR /app

RUN apt-get update -qq && apt-get -y --no-install-recommends install \
    build-essential \
    ca-certificates \
    curl \
    libpq-dev

ENV PID1_VERSION=0.1.3.1
RUN curl -sSL "https://github.com/fpco/pid1/releases/download/v${PID1_VERSION}/pid1" -o /sbin/pid1 && \
    chown root:root /sbin/pid1 && \
    chmod +x /sbin/pid1

COPY docker-entrypoint.sh /usr/local/bin/entrypoint.sh
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY . /app

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

CMD ["gunicorn", "project.wsgi:application", "-b", "0.0.0.0:8000", "-w", "2", "--access-logfile", "-", "--error-logfile", "-", "-c", "/app/gunicorn.config.py"]
