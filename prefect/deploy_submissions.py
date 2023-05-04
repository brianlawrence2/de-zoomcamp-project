from prefect.deployments import Deployment
from prefect.infrastructure import DockerContainer
from etl_submissions_gcs_to_bigquery import etl_gcs_to_bigquery

def deploy():
    docker_container_block = DockerContainer.load("de-zoomcamp-docker-block")
    
    
    deployment = Deployment.build_from_flow(
        flow=etl_gcs_to_bigquery,
        name='etl-gcs-to-bigquery-deployment_submissions',
        infrastructure=docker_container_block
    )
    deployment.apply()
    
if __name__ == '__main__':
    deploy()