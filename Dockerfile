FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml ./
COPY stock_analysis_runtime ./stock_analysis_runtime
RUN pip install --no-cache-dir . && useradd --uid 10001 runtime
USER runtime
VOLUME ["/data"]
ENV STOCK_ANALYSIS_STORAGE=/data
EXPOSE 8080
HEALTHCHECK CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health')"
ENTRYPOINT ["stock-analysis-runtime", "--host", "0.0.0.0"]
