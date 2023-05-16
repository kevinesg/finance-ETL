FROM prefecthq/prefect:2.7.7-python3.9

COPY docker-requirements.txt .

RUN pip install -r docker-requirements.txt --no-cache-dir

COPY credentials ./credentials
COPY flows ./flows

CMD prefect cloud login \
    --key pnu_TknF8R914OMHfWg9K8TTrxXmkEcCgl2kZOlB \
    --workspace kevinesg/kevinesg-workspace; \
    prefect work-pool create finance-workpool; \
    prefect work-pool set-concurrency-limit finance-workpool 1; \
    prefect deployment build flows/main_flow.py:main_flow \
 --name finance_main_deployment \
 --pool finance-workpool \
 --work-queue default \
 --cron "*/10 * * * *" \
 --timezone "Asia/Manila"; \
    prefect deployment apply main_flow-deployment.yaml; \
    prefect agent start --pool finance-workpool --work-queue default