FROM kernai/refinery-parent-images:v1.19.0-common

WORKDIR /app

RUN apt-get update && \
    apt-get install --no-install-recommends -y git && \
    rm -rf /var/lib/apt/lists/*

VOLUME ["/app"]

COPY requirements*.txt .

RUN pip3 install --no-cache-dir -r requirements-dev.txt

COPY / .

CMD [ "/usr/local/bin/uvicorn", "--host", "0.0.0.0", "--port", "80", "app:app", "--reload" ]