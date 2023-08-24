#!/bin/bash

# Mount docker volumes
mount 10.128.17.210:/docker_volumes /var/lib/docker/volumes
echo "10.128.17.210:/docker_volumes /var/lib/docker/volumes nfs auto,nofail,noatime,nolock,intr,tcp,actimeo=1800 0 0" >> /etc/fstab

# Install prerequisite debian packages
apt update && apt upgrade -y
apt install -y nfs-common docker docker-compose git apt-transport-https ca-certificates curl gnupg python3-pip

# Add doppler
curl -sLf --retry 3 --tlsv1.2 --proto "=https" 'https://packages.doppler.com/public/cli/gpg.DE2A7741A397C129.key' | apt-key add -
echo "deb https://packages.doppler.com/public/cli/deb/debian any-version main" > /etc/apt/sources.list.d/doppler-cli.list
apt update && apt install -y doppler

# Create prefect user
adduser prefect
usermod -aG docker prefect

# Restart
reboot