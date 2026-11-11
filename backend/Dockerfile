# stage One: install Tools
FROM python:3.12-slim as tools-builder

# install GO
RUN apt-get update && apt-get install -y \
    git curl wget unzip build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN wget -q https://go.dev/dl/go1.22.5.linux-amd64.tar.gz \
    && tar -C /usr/local -xzf go1.22.5.linux-amd64.tar.gz \
    && rm go1.22.5.linux-amd64.tar.gz

ENV PATH="/usr/local/go/bin:/root/go/bin:${PATH}"

# Install Go-based recon tools from GitHub releases 
RUN go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
RUN go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
RUN go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest
RUN go install -v github.com/projectdiscovery/shuffledns/cmd/shuffledns@latest
RUN go install -v github.com/owasp-amass/amass/v4/cmd/amass@latest
RUN go install -v github.com/tomnomnom/assetfinder@latest
RUN go install -v github.com/OJ/gobuster/v3@latest
RUN go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest

# Runtime
FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y \ 
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=tools-builder /root/go/bin/subfinder /usr/local/bin/
COPY --from=tools-builder /root/go/bin/httpx /usr/local/bin/
COPY --from=tools-builder /root/go/bin/dnsx /usr/local/bin/
COPY --from=tools-builder /root/go/bin/shuffledns /usr/local/bin/
COPY --from=tools-builder /root/go/bin/amass /usr/local/bin/
COPY --from=tools-builder /root/go/bin/assetfinder /usr/local/bin/
COPY --from=tools-builder /root/go/bin/gobuster /usr/local/bin/
COPY --from=tools-builder /root/go/bin/nuclei /usr/local/bin/

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/data

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]