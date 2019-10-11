## appearance

# ZSH_THEME=bira
ZSH_THEME=avit

## extra path
export PATH="$HOME/bin:$PATH"
export PATH="$HOME/.cargo/bin:$PATH"

## plugins

plugins=(git brew)

# fuck
if type thefuck > /dev/null; then
    eval $(thefuck --alias)
fi

## misc configs

# increase number of open files
alias emacs="ulimit -n 16384 && emacs"
# edit in emacs
alias e="emacsclient -n "

# misc alias
alias la="ls -la"

# temperature
alias temperature="sysctl machdep.xcpm.cpu_thermal_level; sysctl machdep.xcpm.gpu_thermal_level"

# mkdir and cd
mcd () {
    mkdir -p -- "$1" && cd -P -- "$1"
}

# cd and ls
cl () {
    cd "$@" && ls;
}

# TODO add config for checking if my projects and configs need sync
