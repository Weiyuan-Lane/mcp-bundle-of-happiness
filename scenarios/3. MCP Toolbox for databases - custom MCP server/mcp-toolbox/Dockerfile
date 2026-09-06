FROM alpine:3.24.1 AS builder

WORKDIR /app
ARG MCP_TOOLBOX_VERSION=1.10.0

RUN apk add --no-cache ca-certificates curl gcompat libstdc++ && \
    curl -L -o /app/toolbox "https://storage.googleapis.com/mcp-toolbox-for-databases/v${MCP_TOOLBOX_VERSION}/linux/amd64/toolbox" && \
    chmod +x /app/toolbox

COPY run.sh /app/run.sh
RUN chmod +x /app/run.sh

ENTRYPOINT [ "/app/run.sh" ]
