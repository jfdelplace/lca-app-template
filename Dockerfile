FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Managed container hosting supplies the port it wants; default for local runs.
ENV PORT=8501
EXPOSE 8501

# Streamlit holds a websocket per browser session, so it must not be run behind anything
# that buffers. Headless mode and a bound address are required in a container.
CMD ["sh", "-c", "streamlit run app.py \
  --server.port=${PORT} \
  --server.address=0.0.0.0 \
  --server.headless=true \
  --browser.gatherUsageStats=false"]
