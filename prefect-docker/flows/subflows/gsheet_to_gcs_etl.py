import os
from pathlib import Path
import gspread as gs
import pandas as pd
from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket
from google.cloud import storage


parameters = {
    'service_account_creds' : './credentials/finance-etl-creds.json',
    'gsheet_url' : 'https://docs.google.com/spreadsheets/d/1iOOfi8ZLbsWp2PsnxW0YctsFCZ9_fK6mZXDVnG993j8',
    'sheet_name' : 'data',
    'raw_data_dir' : './data/raw/',
    'raw_data_file' : 'raw_data.csv',
    'table_name' : 'raw_data',
    'bucket_name': 'kevinesg-finance-bucket',
    'project_id': 'kevinesg-finance'
}

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = parameters['service_account_creds']


@flow(name='gsheet to GCS ETL', log_prints=True)
def gsheet_to_gcs_etl(
    service_account_creds:str=parameters['service_account_creds'],
    gsheet_url:str=parameters['gsheet_url'],
    sheet_name:str=parameters['sheet_name'],
    raw_data_dir:str=parameters['raw_data_dir'],
    raw_data_file:str=parameters['raw_data_file'],
    table_name:str=parameters['table_name'],
    bucket_name:str=parameters['bucket_name'],
    project_id:str=parameters['project_id']
) -> None:

    if not os.path.exists(raw_data_dir):
        os.makedirs(raw_data_dir)

    raw_data_path = Path(raw_data_dir + raw_data_file)

    raw_data = extract_gsheet_data(
        service_account_creds=service_account_creds, 
        gsheet_url=gsheet_url, 
        sheet_name=sheet_name,
        raw_data_path=raw_data_path
    )
    ingest_local(df=raw_data, raw_data_path=raw_data_path)
    ingest_to_gcs(project_id=project_id, bucket_name=bucket_name, raw_data_path=raw_data_path)


@task(log_prints=True)
def extract_gsheet_data(
    service_account_creds:str,
    gsheet_url:str,
    sheet_name:str,
    raw_data_path:Path
) -> pd.DataFrame:
    gc = gs.service_account(filename=service_account_creds)
    sh = gc.open_by_url(gsheet_url)
    ws = sh.worksheet(sheet_name)

    df = pd.DataFrame(ws.get_all_records())
    
    return df


@task(log_prints=True)
def ingest_local(df:pd.DataFrame, raw_data_path:Path) -> None:
    df.to_csv(raw_data_path, index=False)


@task(log_prints=True)
def ingest_to_gcs(project_id:str, bucket_name:str, raw_data_path:Path) -> None:

    gcs_bucket = GcsBucket(bucket=bucket_name)

    # create GCS bucket if it does not exist yet
    client = storage.Client()
    if not client.bucket(bucket_name).exists():
        gcs_bucket.create_bucket(project=project_id)

    gcs_bucket.upload_from_path(raw_data_path, raw_data_path)


if __name__ == '__main__':
    gsheet_to_gcs_etl()