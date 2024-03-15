import logging
from typing import Iterable

from kin_txt_core.messaging.rabbit.dtos import Subscription
from kin_txt_core.reports_building.domain.services.predicting.predictor import IPredictorFactory
from kin_txt_core.reports_building.domain.services.validation.factory_interface import BaseValidatorFactory
from kin_txt_core.reports_building.settings import Settings
from kin_txt_core.reports_building.containers import Container
from kin_txt_core.reports_building import events, domain

__all__ = ["run_consumer"]

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

    container.config.from_dict(settings.dict())
    container.init_resources()

    container.wire(
        packages=[domain, events],
    )

    container.check_dependencies()

    return container


def run_consumer(
    predictor_factory: IPredictorFactory,
    validator_factory: BaseValidatorFactory | None = None,
    additional_subscriptions: Iterable[Subscription] | None = None,
) -> None:
    settings = Settings()
    container = init_containers(settings, predictor_factory, validator_factory, additional_subscriptions)

    container.domain_services.model_type_registration_service().register_model_type()

    _logger.info("Consuming started...")
    container.messaging.subscriber().start_consuming()
