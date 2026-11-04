# File system
if command -v eza &> /dev/null
    alias ls='eza -lh --group-directories-first --icons=auto'
    alias lsa='ls -a'
    alias lt='eza --tree --level=2 --long --icons --git'
    alias lta='lt -a'
end

# fzf preview (detect kitty for image preview)
if test "$TERM" = "xterm-kitty"
    alias ff="fzf --preview 'case (file --mime-type -b {}) in image/*) kitty icat --clear --transfer-mode=memory --stdin=no --place=\${FZF_PREVIEW_COLUMNS}x\${FZF_PREVIEW_LINES}@0x0 {} ;; *) bat --style=numbers --color=always {} ;; esac'"
else
    alias ff="fzf --preview 'bat --style=numbers --color=always {}'"
end
alias eff='$EDITOR (ff)'

function sff
    if test (count $argv) -eq 0
        echo "Usage: sff <destination> (e.g. sff host:/tmp/)"
        return 1
    end
    set file (find . -type f -printf '%T@\t%p\n' | sort -rn | cut -f2- | ff)
    if test -n "$file"
        scp "$file" $argv[1]
    end
end

# zoxide
if command -v zoxide &> /dev/null
    alias cd="zd"
    function zd
        if test (count $argv) -eq 0
            builtin cd ~; or return
        else if test -d $argv[1]
            builtin cd $argv[1]; or return
        else
            if not z $argv
                echo "Error: Directory not found"
                return 1
            end
            printf "\U000F17A9 "
            pwd
        end
    end
end

# open
function open
    xdg-open $argv >/dev/null 2>&1 &
end

# Directories
alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'

# Tools
alias d='docker'
alias t='tmux attach || tmux new -s Work'
alias mup='MISE_MINIMUM_RELEASE_AGE=0 mise up'

function n
    if test (count $argv) -eq 0
        command nvim .
    else
        command nvim $argv
    end
end

# Clear
alias cc='clear'

# Git
alias g='git'
alias gs='git status'
alias ga='git add'
alias gc='git commit'
alias gcm='git commit -m'
alias gcam='git commit -a -m'
alias gcad='git commit -a --amend'
alias gp='git push'
alias gl='git pull'
alias glog='git log --oneline --graph --decorate -20'

# Navigation
alias back='cd -'
alias l='ls'

alias ll='ls'
alias la='ls -a'
alias ocode='env TMPDIR="$HOME/.cache/opencode-tmp" opencode'
alias c='ocode'
