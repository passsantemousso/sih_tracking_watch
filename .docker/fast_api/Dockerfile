FROM python:3.12-slim
LABEL authors="effijeanmermoz"

ENTRYPOINT ["top", "-b"]


WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir fastapi  pydantics transformers uvicorn

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]