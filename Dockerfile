FROM python:3.13-slim

# git gh インストール
RUN apt-get update && \
    apt-get install -y git curl && \
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg && \
    chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null && \
    apt-get update && \
    apt-get install -y gh && \
    rm -rf /var/lib/apt/lists/*

# Mecab
RUN apt update && apt install -y mecab mecab-ipadic-utf8 libmecab-dev
# 以下も必要だった
# ln -sf /usr/local/lib/python3.13/site-packages/ipadic/dicdir/mecabrc /usr/local/etc/mecabrc

CMD [ "bash" ]