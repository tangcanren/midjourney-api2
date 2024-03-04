FROM python:3.11-bullseye

WORKDIR /mdt/run

RUN pip install --no-cache-dir poetry==1.7.1 && \
    poetry config virtualenvs.create false
COPY app.py pyproject.toml poetry.lock banned_words.txt ./
COPY lib ./lib
COPY task ./task
COPY util ./util
RUN poetry install

ENTRYPOINT ["uvicorn", "app:app", "--host", "0.0.0.0"]
EXPOSE 8000
