FROM python:3.12.11-bookworm

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install uv --no-cache-dir
RUN uv pip install --no-cache-dir --system -r requirements.txt
RUN rm requirements.txt

COPY . .

EXPOSE 8501

ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]