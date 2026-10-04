FROM node:22.20.0-bookworm-slim@sha256:b21fe589dfbe5cc39365d0544b9be3f1f33f55f3c86c87a76ff65a02f8f5848e AS base
ARG AGENT_UID=1001
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 ca-certificates curl git bubblewrap ripgrep \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid ${AGENT_UID} --shell /bin/bash agent \
    && mkdir /work && touch /work/.env && chown agent:agent /work
LABEL modelspec.agent_uid="${AGENT_UID}"
COPY entrypoint.py gemini-settings.mjs gemini-isolated.json gemini-positive.json /opt/modelspec-harness/
ENV HOME=/home/agent
USER agent
WORKDIR /work
ENTRYPOINT ["python3", "/opt/modelspec-harness/entrypoint.py"]

FROM base AS ux-base
USER root
# Pin the official server and its Chromium build; only UX targets carry browsers.
RUN npm install --prefix /opt/modelspec-browser --no-audit --no-fund @playwright/mcp@0.0.83 \
    && PLAYWRIGHT_BROWSERS_PATH=/opt/modelspec-browser/browsers \
       /opt/modelspec-browser/node_modules/.bin/playwright install --with-deps chromium --only-shell \
    && chmod -R a+rX /opt/modelspec-browser && npm cache clean --force \
    && rm -rf /var/lib/apt/lists/*
COPY ux-mcp.mjs /opt/modelspec-harness/

FROM ux-base AS claude-ux
ARG CLI_VERSION
RUN npm install --global --no-audit --no-fund @anthropic-ai/claude-code@${CLI_VERSION} && npm cache clean --force
LABEL modelspec.cli="claude" modelspec.cli_version="${CLI_VERSION}"
USER agent

FROM ux-base AS codex-ux
ARG CLI_VERSION
RUN npm install --global --no-audit --no-fund @openai/codex@${CLI_VERSION} && npm cache clean --force
LABEL modelspec.cli="codex" modelspec.cli_version="${CLI_VERSION}"
USER agent

FROM ux-base AS gemini-ux
ARG CLI_VERSION
RUN npm install --global --no-audit --no-fund @google/gemini-cli@${CLI_VERSION} && npm cache clean --force
LABEL modelspec.cli="gemini" modelspec.cli_version="${CLI_VERSION}"
USER agent

FROM ux-base AS grok-ux
ARG CLI_VERSION
ARG TARGETARCH
RUN case "$TARGETARCH" in arm64) arch=aarch64 ;; amd64) arch=x86_64 ;; *) exit 1 ;; esac \
    && curl --fail --show-error --location --proto '=https' "https://x.ai/cli/grok-${CLI_VERSION}-linux-${arch}.gz" -o /tmp/grok.gz \
    && gzip -dc /tmp/grok.gz > /usr/local/bin/grok && chmod 755 /usr/local/bin/grok && rm /tmp/grok.gz
LABEL modelspec.cli="grok" modelspec.cli_version="${CLI_VERSION}"
USER agent

FROM base AS claude
USER root
ARG CLI_VERSION
RUN npm install --global --no-audit --no-fund @anthropic-ai/claude-code@${CLI_VERSION} \
    && npm cache clean --force
LABEL modelspec.cli="claude" modelspec.cli_version="${CLI_VERSION}"
USER agent

FROM base AS codex
USER root
ARG CLI_VERSION
RUN npm install --global --no-audit --no-fund @openai/codex@${CLI_VERSION} \
    && npm cache clean --force
LABEL modelspec.cli="codex" modelspec.cli_version="${CLI_VERSION}"
USER agent

FROM base AS gemini
USER root
ARG CLI_VERSION
RUN npm install --global --no-audit --no-fund @google/gemini-cli@${CLI_VERSION} \
    && npm cache clean --force
LABEL modelspec.cli="gemini" modelspec.cli_version="${CLI_VERSION}"
USER agent

FROM base AS grok
USER root
ARG CLI_VERSION
ARG TARGETARCH
# Versioned public artifact URLs come from xAI's official Linux installer.
RUN case "$TARGETARCH" in arm64) arch=aarch64 ;; amd64) arch=x86_64 ;; *) exit 1 ;; esac \
    && curl --fail --show-error --location --proto '=https' \
       "https://x.ai/cli/grok-${CLI_VERSION}-linux-${arch}.gz" -o /tmp/grok.gz \
    && gzip -dc /tmp/grok.gz > /usr/local/bin/grok \
    && chmod 755 /usr/local/bin/grok && rm /tmp/grok.gz
LABEL modelspec.cli="grok" modelspec.cli_version="${CLI_VERSION}"
USER agent
