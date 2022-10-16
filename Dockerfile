FROM python:3
WORKDIR /usr/src/app
COPY . .

RUN apt upgrade
RUN apt install -y ffmpeg
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir matplotlib numpy discord pyyaml && \
    pip install --no-cache-dir asyncio importlib pytube

CMD ["Nomitron.py"]
ENTRYPOINT ["python3"]
