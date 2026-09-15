# benchgraph graph: FalkorDB + a read-only HTTP query service (MODEL-9).
# Build from the repository root:
#   docker build -f graph-service/Dockerfile -t benchgraph-graph .
# Disk is ephemeral on Cloudflare Containers: the graph is reloaded from
# GRAPH_EXPORT_URL every time the container starts.
FROM falkordb/falkordb:v4.20.1

RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 python3-venv ca-certificates \
 && rm -rf /var/lib/apt/lists/* \
 && python3 -m venv /opt/graph \
 && /opt/graph/bin/pip install --no-cache-dir "FalkorDB==1.7.1"

WORKDIR /opt/graph/app
COPY pipeline/__init__.py pipeline/benchgraph_graph.py pipeline/
COPY graph-service/service.py graph-service/start.sh ./
RUN chmod +x start.sh

# No browser UI, FalkorDB bound to loopback: only the query service is reachable.
ENV BROWSER=0 \
    PORT=8080 \
    FALKORDB_HOST=127.0.0.1 \
    FALKORDB_PORT=6379 \
    PYTHONPATH=/opt/graph/app
EXPOSE 8080

ENTRYPOINT ["/opt/graph/app/start.sh"]
