FROM python:3.11.1

WORKDIR /app
COPY encoders.py encoders.py
COPY get_subreddit_stream.py get_subreddit_stream.py
COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "get_subreddit_stream.py" ]