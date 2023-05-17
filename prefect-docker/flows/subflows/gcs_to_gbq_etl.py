import os
import pandas as pd
from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket
from prefect_gcp import GcpCredentials
from google.cloud import bigquery


parameters = {
    'service_account_creds' : './credentials/finance-etl-creds.json',
    'raw_data_dir' : '/data/raw/',
    'raw_data_file' : 'raw_data.csv',
    'prefect_gcs_bucket_name' : 'kevinesg-finance-bucket',
    'gcs_bucket_creds' : 'finance-etl-creds',
    'project_id' : 'kevinesg-finance',
    'schema_table' : 'finance.raw_data',
    'gbq_dataset': 'finance',
    'gbq_table': 'raw_data'
}

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = parameters['service_account_creds']


@flow(name='GCS to GBQ ETL', log_prints=True)
def gcs_to_gbq_etl(
    service_account_creds:str=parameters['service_account_creds'],
    raw_data_dir:str=parameters['raw_data_dir'], 
    raw_data_file:str=parameters['raw_data_file'], 
    prefect_gcs_bucket_name:str=parameters['prefect_gcs_bucket_name'], 
    gcs_bucket_creds:str=parameters['gcs_bucket_creds'],
    project_id:str=parameters['project_id'],
    gbq_dataset:str=parameters['gbq_dataset'],
    gbq_table:str=parameters['gbq_table']
    ):

    raw_data_path = raw_data_dir + raw_data_file

    df = extract_from_gcs(
        raw_data_path=raw_data_path, 
        prefect_gcs_bucket_name=prefect_gcs_bucket_name,
        gcs_path=raw_data_path
    )
    ingest_to_gbq(
        df=df,
        service_account_creds=service_account_creds,
        project_id=project_id,
        gbq_dataset=gbq_dataset,
        gbq_table=gbq_table
    )


@task(log_prints=True)
def extract_from_gcs(raw_data_path:str, prefect_gcs_bucket_name:str, gcs_path:str) -> pd.DataFrame:

    df = pd.read_csv(f'gs://{prefect_gcs_bucket_name}{raw_data_path}')

    return df


@task(log_prints=True)
def ingest_to_gbq(
    df:pd.DataFrame, service_account_creds:str, project_id:str, gbq_dataset:str, gbq_table:str
    ) -> None:

    bq_client = bigquery.Client(project=project_id)

    datasets = list(bq_client.list_datasets())
    dataset_ids = [dataset.dataset_id for dataset in datasets]
    
    if gbq_dataset not in dataset_ids:
        dataset = bq_client.create_dataset(bigquery.Dataset(bq_client.dataset(gbq_dataset)))

    gcp_credentials = GcpCredentials(service_account_file=service_account_creds)

    df.to_gbq(
        destination_table=f'{gbq_dataset}.{gbq_table}',
        project_id=project_id,
        credentials=gcp_credentials.get_credentials_from_service_account(),
        chunksize=500_000,
        if_exists='replace'
    )


if __name__ == '__main__':
    gcs_to_gbq_etl()