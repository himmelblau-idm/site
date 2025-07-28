FROM debian:bookworm

# Install required tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        apt-utils \
        dpkg-dev \
        curl \
        jq \
        gzip \
        ca-certificates \
        && rm -rf /var/lib/apt/lists/*

# Add your script
COPY genrepo.sh /genrepo.sh
RUN chmod +x /genrepo.sh

# Entrypoint to allow passing in GPG info if needed
ENTRYPOINT ["/genrepo.sh"]
