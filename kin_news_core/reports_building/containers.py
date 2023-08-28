from dependency_injector import providers, containers, resources

from kin_news_core.messaging import AbstractEventSubscriber, AbstractEventProducer
from kin_news_core.messaging.rabbit import RabbitProducer, RabbitClient, RabbitSubscriber
from kin_news_core.reports_building.domain.services import GenerateRequestHandlerService
from kin_news_core.reports_building.domain.services.predicting.predictor import IPredictorFactory
from kin_news_core.reports_building.domain.services.validation.factory_interface import BaseValidatorFactory
from kin_news_core.telegram import TelegramClientProxy
from kin_news_core.reports_building.infrastructure.services import StatisticsService, ModelTypesService
from kin_news_core.reports_building.events import GenerateReportRequestOccurred
from kin_news_core.reports_building.domain.services.validation import ModelValidationService
from kin_news_core.reports_building.domain.services.statistical_report.generate_statistical_report import GenerateStatisticalReportService
from kin_news_core.reports_building.domain.services.word_cloud.generate_word_cloud_report import GenerateWordCloudReportService
from kin_news_core.reports_building.constants import REPORTS_BUILDER_EXCHANGE


class SubscriberResource(resources.Resource):
    def init(self, client: RabbitClient) -> AbstractEventSubscriber:
        subscriber = RabbitSubscriber(client=client)

        from kin_news_core.reports_building.events.handlers import (
            on_report_processing_request,
        )

        subscriber.subscribe(REPORTS_BUILDER_EXCHANGE, GenerateReportRequestOccurred, on_report_processing_request)

        return subscriber


class Messaging(containers.DeclarativeContainer):
    config = providers.Configuration()

    rabbitmq_client: providers.Singleton[RabbitClient] = providers.Singleton(
        RabbitClient,
        connection_string=config.rabbitmq_connection_string,
    )

    producer: providers.Singleton[AbstractEventProducer] = providers.Singleton(
        RabbitProducer,
        client=rabbitmq_client,
    )

    subscriber: providers.Resource[AbstractEventSubscriber] = providers.Resource(
        SubscriberResource,
        client=rabbitmq_client,
    )


class Clients(containers.DeclarativeContainer):
    config = providers.Configuration()

    telegram_client: providers.Factory[TelegramClientProxy] = providers.Factory(
        TelegramClientProxy,
        session_str=config.telegram.session_string,
        api_id=config.telegram.api_id,
        api_hash=config.telegram.api_hash,
    )


class Factories(containers.DeclarativeContainer):
    validator_factory: providers.Singleton[BaseValidatorFactory] = providers.Singleton(
        BaseValidatorFactory,
    )


class Services(containers.DeclarativeContainer):
    config = providers.Configuration()

    statistics_service: providers.Singleton[StatisticsService] = providers.Singleton(
        StatisticsService,
        url=config.statistics_service,
        kin_token=config.kin_token,
    )

    model_types_service: providers.Singleton[ModelTypesService] = providers.Singleton(
        ModelTypesService,
        url=config.statistics_service,
        kin_token=config.kin_token,
    )


class DomainServices(containers.DeclarativeContainer):
    config = providers.Configuration()
    clients = providers.DependenciesContainer()
    services = providers.DependenciesContainer()
    messaging = providers.DependenciesContainer()
    factories = providers.DependenciesContainer()
    predictor_factory: IPredictorFactory = providers.Object()

    model_validation_service: providers.Singleton[ModelValidationService] = providers.Singleton(
        ModelValidationService,
        events_producer=messaging.producer,
        validator_factory=factories.validator_factory,
    )

    generate_request_handler_service: providers.Singleton[GenerateRequestHandlerService] = providers.Singleton(
        GenerateRequestHandlerService,
        predictor_factory=predictor_factory,
        model_types_service=services.model_types_service,
    )

    generate_statistics_report_service: providers.Singleton[GenerateStatisticalReportService] = providers.Singleton(
        GenerateStatisticalReportService,
        telegram_client=clients.telegram_client,
        events_producer=messaging.producer,
        statistics_service=services.statistics_service,
        model_types_service=services.model_types_service,
        predictor_factory=predictor_factory,
    )

    generate_word_cloud_report_service: providers.Singleton[GenerateWordCloudReportService] = providers.Singleton(
        GenerateWordCloudReportService,
        telegram_client=clients.telegram_client,
        events_producer=messaging.producer,
        statistics_service=services.statistics_service,
        model_types_service=services.model_types_service,
        predictor_factory=predictor_factory,
    )


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    predictor_factory: IPredictorFactory = providers.Object()

    messaging: providers.Container[Messaging] = providers.Container(
        Messaging,
        config=config,
    )

    clients: providers.Container[Clients] = providers.Container(
        Clients,
        config=config,
    )

    services: providers.Container[Services] = providers.Container(
        Services,
        config=config,
    )

    factories: providers.Container[Factories] = providers.Container(
        Factories,
    )

    domain_services: providers.Container[DomainServices] = providers.Container(
        DomainServices,
        config=config,
        clients=clients,
        services=services,
        messaging=messaging,
        factories=factories,
        predictor_factory=predictor_factory,
    )
