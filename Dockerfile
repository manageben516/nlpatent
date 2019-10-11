FROM python:2-slim-stretch

WORKDIR /legalicity/nlpatent

COPY . ./
RUN set -x \
    && apt-get update \
    && apt-get install --no-install-recommends --no-install-suggests -y build-essential \
    && groupadd -g 1000 legalicity \
    && useradd -d /legalicity/nlpatent -g legalicity -s /bin/bash -u 1000 legalicity \
    && pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

USER legalicity

CMD ["gunicorn", \
     "-b", "0.0.0.0:5000", \
     "-w", "8", \
     "-t", "600", \
     "nlpatent:app"]
