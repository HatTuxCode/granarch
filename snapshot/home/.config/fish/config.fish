# Disable welcome message
set -g fish_greeting ""

# Short alias for opencode
alias ocode=opencode

# Match Bash's prompt using the shared Starship configuration.
if status is-interactive; and test "$TERM" != dumb; and command -q starship
    starship init fish | source
end

# Use terminal colors (Gran theme handles this via terminal config)
# Fish will inherit the terminal's 16-color palette automatically

# Optional: If you want to customize fish's syntax highlighting colors
# to match the theme more precisely, uncomment and adjust:
# set -g fish_color_autosuggestion 555
# set -g fish_color_command 0xff79c6
# set -g fish_color_comment 0x6272a4
# set -g fish_color_cwd green
# set -g fish_color_cwd_root red
# set -g fish_color_end 0xff79c6
# set -g fish_color_error 0xff5555
# set -g fish_color_escape 0xff79c6
# set -g fish_color_match --background=brblue
# set -g fish_color_normal normal
# set -g fish_color_operator 0xff79c6
# set -g fish_color_param 0xf8f8f2
# set -g fish_color_quote 0xf1fa8c
# set -g fish_color_redirection 0xff79c6
# set -g fish_color_search_match --background=brblack
# set -g fish_color_selection --background=brblack
# set -g fish_color_status red
# set -g fish_color_user brgreen
# set -g fish_color_host normal
# set -g fish_color_cancel -r
# set -g fish_color_valid_path --underline
