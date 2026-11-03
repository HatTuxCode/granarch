#!/usr/bin/env bash
# Stage 3 of install.sh: install the terminal tools and require a working OpenCode.
set -euo pipefail
mise use -g node@lts
mise use -g npm:@openai/codex@latest
gran-opencode-install
mise reshim
opencode --version
