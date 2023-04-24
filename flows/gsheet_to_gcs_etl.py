import gspread as gs
import pandas as pd
from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket


parameters = {
    'gspread_auth' : './credentials/gspread-auth.json',
    'gsheet_url' : 'https://docs.google.com/spreadsheets/d/1iOOfi8ZLbsWp2PsnxW0YctsFCZ9_fK6mZXDVnG993j8',
    'sheet_name' : 'data',
    'raw_data_dir' : './data/raw/',
    'raw_data_file' : 'raw_data.csv',
    'table_name' : 'raw_data',
    'gcs_bucket_name' : 'finance-etl'
}


@flow(name='gsheet-to-gcs-etl', log_prints=True)
def gsheet_to_gcs_etl(
    gspread_auth:str=parameters['gspread_auth'],
    gsheet_url:str=parameters['gsheet_url'],
    sheet_name:str=parameters['sheet_name'],
    raw_data_dir:str=parameters['raw_data_dir'],
    raw_data_file:str=parameters['raw_data_file'],
    table_name:str=parameters['table_name'],
    gcs_bucket_name:str=parameters['gcs_bucket_name']
) -> None:

    raw_data_path = raw_data_dir + raw_data_file

    raw_data = extract_gsheet_data(
        gspread_auth=gspread_auth, 
        gsheet_url=gsheet_url, 
        sheet_name=sheet_name,
        raw_data_path=raw_data_path
    )
    ingest_local(df=raw_data, raw_data_path=raw_data_path)
    ingest_to_gcs(gcs_bucket_name=gcs_bucket_name, raw_data_path=raw_data_path)


@task(log_prints=True)
def extract_gsheet_data(
    gspread_auth:str,
    gsheet_url:str,
    sheet_name:str,
    raw_data_path:str
) -> pd.DataFrame:
    gc = gs.service_account(filename=gspread_auth)
    sh = gc.open_by_url(gsheet_url)
    ws = sh.worksheet(sheet_name)

    df = pd.DataFrame(ws.get_all_records())
    
    return df


@task(log_prints=True)
def ingest_local(df:pd.DataFrame, raw_data_path:str) -> None:
    df.to_csv(raw_data_path, index=False)


@task(log_prints=True)
def ingest_to_gcs(gcs_bucket_name:str, raw_data_path:str) -> None:
    gcp_cloud_storage_bucket_block = GcsBucket.load(gcs_bucket_name)
    gcp_cloud_storage_bucket_block.upload_from_path(
        from_path=raw_data_path,
        to_path=raw_data_path
    )


if __name__ == '__main__':
    gsheet_to_gcs_etl()