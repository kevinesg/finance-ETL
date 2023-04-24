import os
import pandas as pd
from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket
from prefect_gcp import GcpCredentials


parameters = {
    'raw_data_dir' : '/data/raw/',
    'raw_data_file' : 'raw_data.csv',
    'prefect_gcs_bucket_name' : 'kevinesg-finance-etl-gcs-bucket',
    'gcs_bucket_creds' : 'finance-etl-creds',
    'project_id' : 'gspread-auth-341206',
    'schema_table' : 'finance.raw_data'
}

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './credentials/' + parameters['gcs_bucket_creds'] + '.json'


@flow(name='gcs-to-gbq-etl', log_prints=True)
def gcs_to_gbq_etl(
    raw_data_dir:str=parameters['raw_data_dir'], 
    raw_data_file:str=parameters['raw_data_file'], 
    prefect_gcs_bucket_name:str=parameters['prefect_gcs_bucket_name'], 
    gcs_bucket_creds:str=parameters['gcs_bucket_creds'],
    project_id:str=parameters['project_id'],
    schema_table:str=parameters['schema_table']
    ):

    raw_data_path = raw_data_dir + raw_data_file

    df = extract_from_gcs(
        raw_data_path=raw_data_path, 
        prefect_gcs_bucket_name=prefect_gcs_bucket_name,
        gcs_path=raw_data_path
    )
    ingest_to_gbq(
        df=df,
        gcs_bucket_creds=gcs_bucket_creds,
        project_id=project_id,
        schema_table=schema_table
    )


@task(log_prints=True)
def extract_from_gcs(raw_data_path:str, prefect_gcs_bucket_name:str, gcs_path:str) -> pd.DataFrame:

    df = pd.read_csv(f'gs://{prefect_gcs_bucket_name}{raw_data_path}')

    return df


@task(log_prints=True)
def ingest_to_gbq(
    df:pd.DataFrame, gcs_bucket_creds:str, project_id:str, schema_table:str) -> None:
    
    gcp_credentials_block = GcpCredentials.load(gcs_bucket_creds)

    df.to_gbq(
        destination_table=schema_table,
        project_id=project_id,
        credentials=gcp_credentials_block.get_credentials_from_service_account(),
        chunksize=500_000,
        if_exists='replace'
    )


if __name__ == '__main__':
    gcs_to_gbq_etl(
    raw_data_dir=parameters['raw_data_dir'], 
    raw_data_file=parameters['raw_data_file'], 
    prefect_gcs_bucket_name=parameters['prefect_gcs_bucket_name'], 
    gcs_bucket_creds=parameters['gcs_bucket_creds'],
    project_id=parameters['project_id'],
    schema_table=parameters['schema_table']
    )