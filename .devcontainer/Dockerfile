FROM mcr.microsoft.com/devcontainers/python:1-3.12-bullseye

# Install PostgreSQL client and uv in a single layer to reduce build time
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends postgresql-client sudo \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# Install uv for vscode user
USER vscode
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/home/vscode/.cargo/bin:${PATH}"

# Set workspace
WORKDIR /workspace
