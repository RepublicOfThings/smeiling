FROM python:3.6.4

EXPOSE 5000

RUN useradd republic

RUN pip install flask gunicorn requests

COPY /vodademo /app

WORKDIR /app

ENV SUBPATH="/vodademo-app"

ENTRYPOINT ["gunicorn", "app:app", "--bind", "0.0.0.0:5000", "--log-level=debug", "--threads=1", "--workers=1", "--timeout=30"]
