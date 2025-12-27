# Gitpod Docker image with Docker-in-Docker support
FROM gitpod/workspace-full

USER gitpod

# Install Docker Compose v2
RUN mkdir -p ~/.docker/cli-plugins && \
    curl -SL https://github.com/docker/compose/releases/download/v2.23.3/docker-compose-linux-x86_64 -o ~/.docker/cli-plugins/docker-compose && \
    chmod +x ~/.docker/cli-plugins/docker-compose

# Install Helm
RUN curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Install kubectl
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" && \
    chmod +x kubectl && \
    sudo mv kubectl /usr/local/bin/

# Pre-pull common Python packages
RUN pip install cryptography psycopg2-binary django
