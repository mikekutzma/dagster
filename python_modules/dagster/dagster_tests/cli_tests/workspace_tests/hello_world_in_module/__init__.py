from dagster._core.definitions import pipeline, repository
from dagster import op


@op
def hello_world(_):
    pass


@pipeline
def hello_world_pipeline():
    hello_world()


@repository
def hello_world_repository():
    return [hello_world_pipeline]
