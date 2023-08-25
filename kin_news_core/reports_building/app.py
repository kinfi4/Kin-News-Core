import logging
from typing import Type

from kin_news_core.reports_building.domain.services.predicting.predictor import IPredictorFactory
from kin_news_core.reports_building.settings import Settings
from kin_news_core.reports_building.containers import Container
from kin_news_core.reports_building import tasks
from kin_news_core.reports_building import events, domain

_logger = logging.getLogger(__name__)


def init_containers(settings: Settings, predictor_factory_class: Type[IPredictorFactory]) -> Container:
    container = Container(predictor_factory_class=predictor_factory_class)
    container.config.from_pydantic(settings)
    container.init_resources()

    container.wire(
        packages=[domain, events],
        modules=[tasks],
    )

    container.check_dependencies()

    return container


def run_celery(predictor_factory_class: Type[IPredictorFactory]) -> None:
    settings = Settings()
    _ = init_containers(settings, predictor_factory_class)

    from kin_news_core.reports_building.tasks import celery_app

    celery_app.worker_main(
        ["worker", "-l", "info"]
    )


def run_consumer(predictor_factory_class: Type[IPredictorFactory]) -> None:
    settings = Settings()
    container = init_containers(settings, predictor_factory_class)

    _logger.info("Consuming started...")
    container.messaging.subscriber().start_consuming()
