#!/usr/bin/env bash
# Publish only project sources to the exact repository authorized by the owner.
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
REMOTE=https://github.com/HatTuxCode/granarch.git
command -v gh >/dev/null || { echo 'O GitHub CLI (gh) é necessário para autenticar o envio.' >&2; exit 1; }
if ! gh auth status -h github.com >/dev/null 2>&1; then
  gh auth login -h github.com --git-protocol https --web
fi
mkdir -p "$ROOT/.publication"
STAGING=$(mktemp -d "$ROOT/.publication/upload.XXXXXX")
git_auth() { git -c credential.helper= -c 'credential.https://github.com.helper=!gh auth git-credential' "$@"; }
git_auth clone "$REMOTE" "$STAGING/repo"
cd "$STAGING/repo"
if git show-ref --verify --quiet refs/remotes/origin/main; then
  git switch main
elif [[ $(git branch --show-current) != main ]]; then
  git switch -c main
fi
python "$ROOT/scripts/prepare-publication.py" --destination "$STAGING/repo"
# Keep commit identity local to the publication clone.
if ! git var GIT_AUTHOR_IDENT >/dev/null 2>&1; then
  identity=$(gh api user --jq '[.login, (.id|tostring)] | @tsv')
  IFS=$'\t' read -r login account_id <<< "$identity"
  [[ $login =~ ^[A-Za-z0-9-]+$ && $account_id =~ ^[0-9]+$ ]] || {
    echo 'Não consegui identificar a conta GitHub para o commit.' >&2; exit 1;
  }
  git config user.name "$login"
  git config user.email "$account_id+$login@users.noreply.github.com"
fi
git add -- README.md .gitignore install.sh docs manifests scripts skills snapshot overlay licenses tests
if ! git diff --cached --quiet; then
  git diff --cached --stat
  git commit -m 'Prepare GranArch installer for minimal EndeavourOS'
fi
git_auth push origin HEAD:main
printf '\nProjeto publicado: https://github.com/HatTuxCode/granarch\n'
printf 'Cópia Git para próximos commits: %s/repo\n' "$STAGING"
