## Setup

- MacOS:
    - Install [brew](https://brew.sh/)
    - Install coreutils
        - `brew install coreutils`
- Install [zsh](https://github.com/ohmyzsh/ohmyzsh/wiki/Installing-ZSH) (may already be pre-installed on mac)
    - MacOS: `brew install zsh`
    - Linux:
        - `sudo apt install zsh`
        - Set as default shell: `chsh -s $(which zsh)` (need to login again)
- Install [oh-my-zsh](https://ohmyz.sh/#install)
    - `sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"`
- Install [fzf](https://github.com/junegunn/fzf)
    - MacOS: `brew install fzf`
    - Linux: `sudo apt install fzf`
- Install [thefuck](https://github.com/nvbn/thefuck)
    - MacOS: `brew install thefuck`
    - Linux: `sudo apt install thefuck`
- Install [eza](https://github.com/eza-community/eza)
    - `brew install eza`
- Install [powerlevel10k](https://github.com/romkatv/powerlevel10k)
    - `git clone --depth=1 https://github.com/romkatv/powerlevel10k.git "${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k"`
    - [Install font manually](https://github.com/romkatv/powerlevel10k?tab=readme-ov-file#manual-font-installation)
        - Linux: [Manual font installation guide](https://github.com/romkatv/powerlevel10k?tab=readme-ov-file#manual-font-installation)
            - Download the fonts to `~/Downloads`
            - Run
                ```
                sudo mkdir -p /usr/share/fonts/truetype/meslolgs-nf
                sudo mv ~/Downloads/Meslo*.ttf /usr/share/fonts/truetype/meslolgs-nf
                sudo fc-cache -fv
                ```
                (Seems like no need to follow instruction for wezterm)
- Install plugins (using zsh)
    - `git clone https://github.com/zsh-users/zsh-autosuggestions.git "${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-autosuggestions"`
    - `git clone https://github.com/zdharma-continuum/fast-syntax-highlighting.git "${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/fast-syntax-highlighting"`
    - `git clone --depth 1 -- https://github.com/marlonrichert/zsh-autocomplete.git "${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autocomplete"`
    - `git clone https://www.github.com/KulkarniKaustubh/fzf-dir-navigator "${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/fzf-dir-navigator"`
- Install dependencies for Python scripts
    - Install [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Install `tommyx_py_utils`
    - See https://github.com/TommyX12/tommyx-utils
- Install shell GPT
    - MacOS: `pipx install shell-gpt` (may need `brew install pipx`)
    - Linux: `pip3 install shell-gpt`
    - Ensure `export OPENAI_API_KEY=<your-openai-api-key>` is in `~/.zshrc`
- Add to `~/.zshrc` (replacing existing setup parts):
    - `source ~/data/tommyx-shell/tommyx-shell.sh`
    - `export PATH="$PATH:$HOME/data/tommyx-shell/scripts"` (note: use `$HOME` instead of `~` in the path)
- Install lazygit
    - `brew install lazygit` (MacOS)
