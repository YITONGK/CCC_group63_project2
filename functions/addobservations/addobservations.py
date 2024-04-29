import logging, json
from flask import current_app, request
from elasticsearch8 import Elasticsearch


def main():
    client = Elasticsearch(
        "https://elasticsearch-master.elastic.svc.cluster.local:9200",
        verify_certs=False,
        basic_auth=("elastic", "elastic"),
    )

    current_app.logger.info(f"Observations to add:  {request.get_json(force=True)}")

    for obs in request.get_json(force=True):
        res = client.index(index="weather", body=obs)
        current_app.logger.info("A new observation has been added. ")

    return "ok"
