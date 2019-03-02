## appearance

ZSH_THEME=bira

## plugins

plugins=(git brew)

## misc configs

# open emacs
alias e="emacsclient -n "

# misc alias
alias la="ls -la"

# mkdir and cd
mkcdir () {
    mkdir -p -- "$1" && cd -P -- "$1"
}

# TODO add config for checking if my projects and configs need sync
