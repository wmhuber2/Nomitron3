FROM python:3
WORKDIR /usr/src/app
COPY . .

RUN apt update
RUN apt install -y ffmpeg
RUN pip install --no-cache-dir --upgrade pip pynacl && \
    pip install --no-cache-dir matplotlib numpy discord pyyaml && \
    pip install --no-cache-dir asyncio importlib youtube_dl pytube

CMD ["Nomitron.py"]
ENTRYPOINT ["python3"]
