from fastapi import APIRouter, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    generate_latest,
)

router = APIRouter()

registry = CollectorRegistry()
rtp_observed = Counter(
    "rtp_observed", "Observed Return To Player", registry=registry
)


@router.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(registry), media_type=CONTENT_TYPE_LATEST)
