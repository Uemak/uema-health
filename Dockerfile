FROM python:3.10-slim as builder

WORKDIR /opt

COPY ./pyproject.toml ./poetry.lock* /opt/

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --without dev && \
    rm -rf ~/.cache

FROM python:3.10-slim

COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin/streamlit /usr/local/bin/streamlit

WORKDIR app
COPY ./uema_health ./

ENV PYTHONUNBUFFERED True

CMD streamlit run main.py \
    --browser.serverAddress="0.0.0.0" \
    --server.port="8080"
