from subflows.gsheet_to_gcs_etl import gsheet_to_gcs_etl
from subflows.gcs_to_gbq_etl import gcs_to_gbq_etl
from prefect import flow


@flow(name='finance main flow', log_prints=True)
def main_flow() -> None:

    subflow_1 = gsheet_to_gcs_etl()
    subflow_2 = gcs_to_gbq_etl(wait_for=[subflow_1])


if __name__ == '__main__':
    
    main_flow()