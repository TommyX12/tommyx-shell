#!/bin/bash

set -euxo pipefail

if [[ "$EUID" -ne 0 ]]; then
    echo "This script must be run as root" >&2
    exit 1
fi

# dependencies

## apt packages

apt update
apt install \
    git \
    vifm \
    ripgrep \
    fd-find \
    btop \
    zsh \
    eza \
    -y

## oh-my-zsh

sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended

## fzf (must be after oh-my-zsh)

git clone --depth 1 https://github.com/junegunn/fzf.git ~/.fzf
~/.fzf/install --all

## nvim (must be after oh-my-zsh because of PATH update)

arch=$(uname -m)

curl -LO https://github.com/neovim/neovim/releases/latest/download/nvim-linux-${arch}.tar.gz
rm -rf /opt/nvim-linux-${arch}
tar -C /opt -xzf nvim-linux-${arch}.tar.gz
echo "export PATH=\"\$PATH:/opt/nvim-linux-${arch}/bin\"" >> ~/.zshrc

## zellij

arch=$(uname -m)
curl -LO "https://github.com/zellij-org/zellij/releases/latest/download/zellij-${arch}-unknown-linux-musl.tar.gz"
tar -xf zellij-${arch}-unknown-linux-musl.tar.gz
mv zellij /bin/zellij
rm zellij-${arch}-unknown-linux-musl.tar.gz

## lazygit

LAZYGIT_VERSION=$(curl -s "https://api.github.com/repos/jesseduffield/lazygit/releases/latest" | \grep -Po '"tag_name": *"v\K[^"]*')
curl -Lo lazygit.tar.gz "https://github.com/jesseduffield/lazygit/releases/download/v${LAZYGIT_VERSION}/lazygit_${LAZYGIT_VERSION}_Linux_x86_64.tar.gz"
tar xf lazygit.tar.gz lazygit
install lazygit -D -t /usr/local/bin/
rm lazygit.tar.gz lazygit

# data directory

mkdir -p ~/data

# shell

(cd ~/data && git clone https://github.com/TommyX12/tommyx-shell.git)

## plugins

git clone --depth=1 https://github.com/romkatv/powerlevel10k.git "${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k"
git clone https://github.com/zsh-users/zsh-autosuggestions.git "${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-autosuggestions"
git clone https://github.com/zdharma-continuum/fast-syntax-highlighting.git "${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/fast-syntax-highlighting"
git clone --depth 1 -- https://github.com/marlonrichert/zsh-autocomplete.git "${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-autocomplete"
git clone https://www.github.com/KulkarniKaustubh/fzf-dir-navigator "${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/fzf-dir-navigator"

curl -LsSf https://astral.sh/uv/install.sh | sh

echo 'source ~/data/tommyx-shell/tommyx-shell.sh' >> ~/.zshrc
echo 'export PATH="$PATH:$HOME/data/tommyx-shell/scripts"' >> ~/.zshrc

# vifm

(cd ~/data && git clone https://github.com/TommyX12/tommyx-vifm-config.git)

mkdir -p ~/.config/vifm
rm -f ~/.config/vifm/vifmrc
ln -s ~/data/tommyx-vifm-config/vifmrc ~/.config/vifm/vifmrc

# vim

(cd ~/data && git clone https://github.com/TommyX12/tommyx-vimrc.git)

touch ~/.vimrc
echo 'source ~/data/tommyx-vimrc/basic.vim' >> ~/.vimrc

touch ~/.vscodevimrc
echo 'source ~/data/tommyx-vimrc/basic.vim' >> ~/.vscodevimrc
echo 'source ~/data/tommyx-vimrc/basic.vscode.vim' >> ~/.vscodevimrc

mkdir -p ~/.config/nvim
touch ~/.config/nvim/init.lua
echo 'vim.cmd [[source ~/data/tommyx-vimrc/basic.vim]]' >> ~/.config/nvim/init.lua
echo 'dofile(vim.fn.expand("~/data/tommyx-vimrc/nvim.lua"))' >> ~/.config/nvim/init.lua

# zellij

(cd ~/data && git clone https://github.com/TommyX12/tommyx-zellij-config.git)

mkdir -p ~/.config/zellij
rm -f ~/.config/zellij/config.kdl
ln -s ~/data/tommyx-zellij-config/config.kdl ~/.config/zellij/config.kdl

# lazygit

(cd ~/data && git clone https://github.com/TommyX12/tommyx-lazygit-config.git)

mkdir -p ~/.config/lazygit
rm -f ~/.config/lazygit/config.yml
ln -s ~/data/tommyx-lazygit-config/config.yml ~/.config/lazygit/config.yml

# btop

(cd ~/data && git clone https://github.com/TommyX12/tommyx-btop-config.git)

mkdir -p ~/.config/btop
rm -f ~/.config/btop/btop.conf
ln -s ~/data/tommyx-btop-config/btop.conf ~/.config/btop/btop.conf
