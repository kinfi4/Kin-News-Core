from typing import Iterable

from dependency_injector import providers, containers, resources

from kin_news_core.messaging import AbstractEventSubscriber, AbstractEventProducer
from kin_news_core.messaging.rabbit import RabbitProducer, RabbitClient, RabbitSubscriber
from kin_news_core.messaging.rabbit.dtos import Subscription
from kin_news_core.reports_building.domain.services import GenerateRequestHandlerService
from kin_news_core.reports_building.domain.services.datasources.factory import DataSourceFactory
from kin_news_core.reports_building.domain.services.datasources.interface import IDataSourceFactory
from kin_news_core.reports_building.domain.services.model_registration import ModelTypeRegistrationService
from kin_news_core.reports_building.domain.services.predicting.predictor import IPredictorFactory
from kin_news_core.reports_building.domain.services.validation.factory_interface import BaseValidatorFactory
from kin_news_core.reports_building.infrastructure.services import StatisticsService, ModelTypesService
from kin_news_core.reports_building.events import GenerateReportRequestOccurred, ModelValidationRequestOccurred
from kin_news_core.reports_building.domain.services.validation import ModelValidationService
from kin_news_core.reports_building.domain.services.statistical_report.generate_statistical_report import GenerateStatisticalReportService
from kin_news_core.reports_building.domain.services.word_cloud.generate_word_cloud_report import GenerateWordCloudReportService
from kin_news_core.reports_building.constants import REPORTS_BUILDER_EXCHANGE


class SubscriberResource(resources.Resource):
    def init(
        self,
        client: RabbitClient,
        additional_subscriptions: Iterable[Subscription] | None = None,
    ) -> AbstractEventSubscriber:
        subscriber = RabbitSubscriber(client=client)

        from kin_news_core.reports_building.events.handlers import (
            on_report_processing_request,
            on_model_validation_request,
        )

        subscriber.subscribe(REPORTS_BUILDER_EXCHANGE, GenerateReportRequestOccurred, on_report_processing_request)
        subscriber.subscribe(REPORTS_BUILDER_EXCHANGE, ModelValidationRequestOccurred, on_model_validation_request)

        if additional_subscriptions is not None:
            for subscription in additional_subscriptions:
                subscriber.subscribe(subscription.aggregate_type, subscription.event_class, subscription.callback)

        return subscriber


class Messaging(containers.DeclarativeContainer):
    config = providers.Configuration()
    additional_subscriptions: list[Subscription] = providers.List()

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
        additional_subscriptions=additional_subscriptions,
    )


class Factories(containers.DeclarativeContainer):
    validator_factory: providers.Singleton[BaseValidatorFactory] = providers.Singleton(
        BaseValidatorFactory,
    )

    datasource_factory: providers.Singleton[IDataSourceFactory] = providers.Singleton(
        DataSourceFactory,
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
        url=config.model_types_service_url,
        kin_token=config.kin_token,
    )


class DomainServices(containers.DeclarativeContainer):
    config = providers.Configuration()
    services = providers.DependenciesContainer()
    messaging = providers.DependenciesContainer()
    factories = providers.DependenciesContainer()
    predictor_factory: IPredictorFactory = providers.Object()

    model_validation_service: providers.Singleton[ModelValidationService] = providers.Singleton(
        ModelValidationService,
        events_producer=messaging.producer,
        validator_factory=factories.validator_factory,
    )

    model_type_registration_service: providers.Singleton[ModelTypeRegistrationService] = providers.Singleton(
        ModelTypeRegistrationService,
        predictor_factory=predictor_factory,
        model_types_service=services.model_types_service,
    )

    generate_request_handler_service: providers.Singleton[GenerateRequestHandlerService] = providers.Singleton(
        GenerateRequestHandlerService,
        predictor_factory=predictor_factory,
        model_types_service=services.model_types_service,
    )

    generate_statistics_report_service: providers.Singleton[GenerateStatisticalReportService] = providers.Singleton(
        GenerateStatisticalReportService,
        events_producer=messaging.producer,
        statistics_service=services.statistics_service,
        model_types_service=services.model_types_service,
        predictor_factory=predictor_factory,
        datasource_factory=factories.datasource_factory,
    )

    generate_word_cloud_report_service: providers.Singleton[GenerateWordCloudReportService] = providers.Singleton(
        GenerateWordCloudReportService,
        events_producer=messaging.producer,
        statistics_service=services.statistics_service,
        model_types_service=services.model_types_service,
        predictor_factory=predictor_factory,
        datasource_factory=factories.datasource_factory,
    )


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    predictor_factory: IPredictorFactory = providers.Object()

    messaging: providers.Container[Messaging] = providers.Container(
        Messaging,
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
        services=services,
        messaging=messaging,
        factories=factories,
        predictor_factory=predictor_factory,
    )
