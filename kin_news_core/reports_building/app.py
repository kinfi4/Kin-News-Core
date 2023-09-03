import logging
from typing import Iterable

from kin_news_core.messaging.rabbit.dtos import Subscription
from kin_news_core.reports_building.domain.services.predicting.predictor import IPredictorFactory
from kin_news_core.reports_building.domain.services.validation.factory_interface import BaseValidatorFactory
from kin_news_core.reports_building.settings import Settings
from kin_news_core.reports_building.containers import Container
from kin_news_core.reports_building import tasks
from kin_news_core.reports_building import events, domain

__all__ = ["run_celery", "run_consumer"]

_logger = logging.getLogger(__name__)


def init_containers(
    settings: Settings,
    predictor_factory: IPredictorFactory,
    validator_factory: BaseValidatorFactory | None = None,
    additional_subscriptions: Iterable[Subscription] | None = None,
) -> Container:
    container = Container(predictor_factory=predictor_factory)

    if validator_factory is not None:
        container.factories.validator_factory.override(validator_factory)
    if additional_subscriptions is not None:
        container.messaging.additional_subscriptions.override(additional_subscriptions)

    container.config.from_pydantic(settings)
    container.init_resources()

    container.wire(
        packages=[domain, events],
        modules=[tasks],
    )

    container.check_dependencies()

    return container


def run_celery(
    predictor_factory: IPredictorFactory,
    validator_factory: BaseValidatorFactory | None = None,
    celery_run_command: list[str] | None = None,
) -> None:
    if celery_run_command is None:
        celery_run_command = ["worker", "-l", "info"]

    settings = Settings()
    _ = init_containers(settings, predictor_factory, validator_factory)

    from kin_news_core.reports_building.tasks import celery_app

    celery_app.worker_main(celery_run_command)


def run_consumer(
    predictor_factory: IPredictorFactory,
    validator_factory: BaseValidatorFactory | None = None,
    additional_subscriptions: Iterable[Subscription] | None = None,
) -> None:
    settings = Settings()
    container = init_containers(settings, predictor_factory, validator_factory, additional_subscriptions)

    _logger.info("Consuming started...")
    container.messaging.subscriber().start_consuming()
