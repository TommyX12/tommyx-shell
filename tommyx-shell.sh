# Enable Powerlevel10k instant prompt. Should stay close to the top of ~/.zshrc.
# Initialization code that may require console input (password prompts, [y/n]
# confirmations, etc.) must go above this block; everything else may go below.
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

export ZSH="$HOME/.oh-my-zsh"

# set zsh theme
ZSH_THEME="powerlevel10k/powerlevel10k"

# extra path
export PATH="$HOME/bin:$PATH"
export PATH="$HOME/.cargo/bin:$PATH"

# oh-my-zsh plugins
plugins=(
    colored-man-pages
    git
    brew
    zsh-autosuggestions
    fast-syntax-highlighting
    zsh-autocomplete
    fzf-dir-navigator
)

# setup oh-my-zsh
source $ZSH/oh-my-zsh.sh

# setup powerlevel10k
[[ ! -f "${0:a:h}/.p10k.zsh" ]] || source "${0:a:h}/.p10k.zsh"

# fzf key bindings
[ -f ~/.fzf.zsh ] && source ~/.fzf.zsh
[ -f /usr/share/doc/fzf/examples/key-bindings.zsh ] && source /usr/share/doc/fzf/examples/key-bindings.zsh
[ -f /usr/share/doc/fzf/examples/completions.zsh ] && source /usr/share/doc/fzf/examples/completions.zsh
[ -f /opt/homebrew/opt/fzf/shell/key-bindings.zsh ] && source /opt/homebrew/opt/fzf/shell/key-bindings.zsh
[ -f /opt/homebrew/opt/fzf/shell/completion.zsh ] && source /opt/homebrew/opt/fzf/shell/completion.zsh

# fuck
# if type thefuck > /dev/null; then
#     eval $(thefuck --alias f)
# fi

# increase number of open files
alias emacs="ulimit -n 16384 && emacs"
# edit in emacs
alias e="emacsclient -n "

# misc alias
alias l="eza -a"
alias la="eza -la"
alias i="sgpt"
alias f="vifm"
alias v="nvim"
alias g="lazygit"

# temperature
alias temperature="sysctl machdep.xcpm.cpu_thermal_level; sysctl machdep.xcpm.gpu_thermal_level"

# mkdir and cd
mcd () {
    mkdir -p -- "$1" && cd -P -- "$1"
}

# cd and ls
cl () {
    cd "$@" && l;
}

-cd () {
    local base="$HOME/data"
    local sel

    sel="$(
        {
            echo "."       # Add current directory (~/data) as an option
            find "$base" -mindepth 1 -maxdepth 1 -type d | sed "s|$base/||"
        } \
        | sort \
        | fzf --height=40 --layout=reverse --border \
            --preview "ls -la \"$base\"/{}  | head -40" \
            --preview-window=right:50%
    )" || return

    if [[ -n "$sel" ]]; then
        if [[ "$sel" == "." ]]; then
            builtin cd "$base"
        else
            builtin cd "$base/$sel"
        fi
    fi
}

# Shell-GPT integration
_sgpt_zsh_shell() {
    if [[ -n "$BUFFER" ]]; then
        _sgpt_prev_cmd=$BUFFER
        BUFFER+="⌛"
        zle -I && zle redisplay
        BUFFER=$(sgpt --shell <<< "$_sgpt_prev_cmd" --no-interaction)
        zle end-of-line
    fi
}
zle -N _sgpt_zsh_shell
bindkey '^y' _sgpt_zsh_shell

# TODO add config for checking if my projects and configs need sync

# zsh autosuggestion
bindkey '^l' autosuggest-accept

# zsh autocomplete
bindkey '^k' history-incremental-search-backward
bindkey '^j' menu-select
bindkey -M menuselect '^k' reverse-menu-complete
bindkey -M menuselect '^j' menu-complete
bindkey -M menuselect '^M' .accept-line
bindkey -M menuselect '\r' .accept-line
zstyle ':autocomplete:*' default-context history-incremental-search-backward
zstyle ':autocomplete:history-incremental-search-backward:*' list-lines 5

if command -v nvim >/dev/null 2>&1; then
    export EDITOR=nvim
    export VISUAL=nvim
else
    export EDITOR=vim
    export VISUAL=vim
fi

# edit command in vim
bindkey '^e' edit-command-line

# fzf config
export FZF_DEFAULT_OPTS='--border --info=inline --layout=reverse'
export FZF_COMPLETION_TRIGGER='``'
export FZF_COMPLETION_OPTS=$FZF_DEFAULT_OPTS

# This speeds up pasting w/ autosuggest
# https://github.com/zsh-users/zsh-autosuggestions/issues/238
pasteinit() {
    OLD_SELF_INSERT=${${(s.:.)widgets[self-insert]}[2,3]}
    zle -N self-insert url-quote-magic # I wonder if you'd need `.url-quote-magic`?
}

pastefinish() {
    zle -N self-insert $OLD_SELF_INSERT
}
zstyle :bracketed-paste-magic paste-init pasteinit
zstyle :bracketed-paste-magic paste-finish pastefinish

fzf_cmd_widget() {
  emulate -L zsh -o no_aliases
  zle -I  # clear any pending display state before running an external TUI

  local selected
  selected=$(
    print -rl -- ${(k)commands} |
      sort -u |
      fzf --prompt='cmd> ' --height=40% --layout=reverse
  ) || return

  LBUFFER+="${selected} "
  zle reset-prompt   # or: zle redisplay
}
zle -N fzf_cmd_widget
bindkey '^a' fzf_cmd_widget
