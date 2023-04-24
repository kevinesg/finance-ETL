from prefect.deployments import Deployment
from prefect.infrastructure.docker import DockerContainer
from gsheet_to_gcs_etl import gsheet_to_gcs_etl
from gcs_to_gbq_etl import gcs_to_gbq_etl


docker_container_block = DockerContainer.load('docker-finance-etl')

docker_gsheet_to_gcs_etl = Deployment.build_from_flow(
    flow=gsheet_to_gcs_etl, 
    name='docker-gsheet-to-gcs-etl',
    infrastructure=docker_container_block
)
docker_gcs_to_gbq_etl = Deployment.build_from_flow(
    flow=gcs_to_gbq_etl, 
    name='docker-gcs-to-qbq-etl',
    infrastructure=docker_container_block
)


if __name__ == '__main__':
    docker_gsheet_to_gcs_etl.apply()
    docker_gcs_to_gbq_etl.apply()