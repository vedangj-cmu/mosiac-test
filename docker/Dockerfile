FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip python3-venv \
    neovim \
    git \
    ripgrep fd-find jq unzip \
    sudo \
  && rm -rf /var/lib/apt/lists/*

# Useful defaults
ENV LC_ALL=C.UTF-8 LANG=C.UTF-8
WORKDIR /work

# Make sure HOME dirs exist and are owned correctly
RUN mkdir -p /home/ubuntu/.local/state \
    /home/ubuntu/.local/share/nvim/swap \
 && chown -R ubuntu:ubuntu /home/ubuntu/.local

USER ubuntu
