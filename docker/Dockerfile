FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    locales curl gnupg2 lsb-release ca-certificates \
    python3 python3-pip python3-venv \
    neovim \
    git \
    ripgrep fd-find jq unzip \
    sudo

# Useful defaults
ENV LC_ALL=C.UTF-8 LANG=C.UTF-8
WORKDIR /work

# Make sure HOME dirs exist and are owned correctly
RUN chown -R ubuntu:ubuntu /home/ubuntu

# Add ROS 2 apt repo (Jazzy for Noble/24.04)
RUN curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
  | gpg --dearmor -o /usr/share/keyrings/ros-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" \
  > /etc/apt/sources.list.d/ros2.list

# Install ROS 2 (minimal) + rosbag2_py bindings
RUN apt-get update && apt-get install -y --no-install-recommends \
    ros-jazzy-ros-base \
    ros-jazzy-rosbag2-py

# Install Node.js LTS and pnpm globally
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Make ROS environment available in shells
SHELL ["/bin/bash", "-lc"]
RUN echo "source /opt/ros/jazzy/setup.bash" >> /etc/bash.bashrc

USER ubuntu
