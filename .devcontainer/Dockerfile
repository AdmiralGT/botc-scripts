FROM mcr.microsoft.com/devcontainers/python:1-3.12-bullseye

# Install PostgreSQL client and uv in a single layer to reduce build time
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends postgresql-client sudo \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# Install uv for root
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:${PATH}"

# Install uv for vscode user
USER vscode
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/home/vscode/.cargo/bin:${PATH}"

# Install Claude Code CLI
RUN curl -fsSL https://claude.com/install.sh | sh
ENV PATH="/home/vscode/.local/bin:${PATH}"

# Set Python unbuffered mode
ENV PYTHONUNBUFFERED=1

# Set workspace
WORKDIR /workspace
