FROM prefecthq/prefect:2.7.7-python3.9

COPY docker-requirements.txt .

RUN pip install -r docker-requirements.txt --no-cache-dir

COPY flows ./flows
COPY data ./data
COPY credentials ./credentials