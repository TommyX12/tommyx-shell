## misc configs

# open emacs
alias e="emacsclient -n "

# mkdir and cd
mkcdir () {
    mkdir -p -- "$1" && cd -P -- "$1"
}

# TODO add config for checking if my projects and configs need sync
