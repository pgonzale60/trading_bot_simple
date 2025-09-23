# GitHub Codespaces Configuration

This directory contains the development container configuration for running this trading bot in GitHub Codespaces.

## What it provides

- **micromamba**: Fast, lightweight conda package manager
- **Python environment**: Automatically creates the `trading-bot-simple` environment
- **VS Code extensions**: Python, Jupyter, Ruff linter, and development tools
- **Auto-setup**: Runs `python test_bot.py` after environment creation

## Usage

1. Open this repository in GitHub Codespaces
2. Wait for the environment to build (2-3 minutes)
3. The trading bot environment will be ready to use
4. Run `python main.py` to test the trading bot

## What happens during setup

1. Codespaces starts with the micromamba container image
2. Creates conda environment from `environment-simple.yml`
3. Activates the trading-bot-simple environment
4. Runs system tests to verify everything works
5. VS Code is configured with Python development extensions

## Troubleshooting

If the environment doesn't activate automatically:
```bash
micromamba activate trading-bot-simple
python test_bot.py
```

If you need to recreate the environment:
```bash
micromamba env create -f environment-simple.yml -y
```

The environment should work perfectly in Codespaces with internet access for Yahoo Finance data.