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
    git
    brew
    zsh-autosuggestions
    zsh-syntax-highlighting
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

# fuck
if type thefuck > /dev/null; then
    eval $(thefuck --alias f)
fi

# increase number of open files
alias emacs="ulimit -n 16384 && emacs"
# edit in emacs
alias e="emacsclient -n "

# misc alias
alias l="eza -a"
alias la="eza -la"

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

git-branch-select-recent () {
    branches=$(git for-each-ref --sort=-committerdate refs/heads/ --format='%(refname:short)' | head -30)
    branch=$(echo "$branches" | fzf)
    if [ -n "$branch" ]
    then
        git checkout $branch
    else
        echo "No branch selected"
    fi
}

# TODO add config for checking if my projects and configs need sync

# zsh autosuggestion
bindkey '^l' autosuggest-accept

export EDITOR=vim
export VISUAL=vim
