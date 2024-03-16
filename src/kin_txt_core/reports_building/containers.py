from typing import Iterable

from dependency_injector import providers, containers, resources

from kin_txt_core.messaging import AbstractEventSubscriber, AbstractEventProducer
from kin_txt_core.messaging.rabbit import RabbitProducer, RabbitClient, RabbitSubscriber
from kin_txt_core.messaging.rabbit.dtos import Subscription
from kin_txt_core.reports_building.domain.services import GenerateRequestHandlerService
from kin_txt_core.reports_building.domain.services.datasources.factory import DataSourceFactory
from kin_txt_core.reports_building.domain.services.datasources.interface import IDataSourceFactory
from kin_txt_core.reports_building.domain.services.model_registration import ModelTypeRegistrationService
from kin_txt_core.reports_building.domain.services.predicting.predictor import IPredictorFactory
from kin_txt_core.reports_building.domain.services.validation.factory_interface import BaseValidatorFactory
from kin_txt_core.reports_building.infrastructure.services import StatisticsService, ModelTypesService
from kin_txt_core.reports_building.events import GenerateReportRequestOccurred, ModelValidationRequestOccurred
from kin_txt_core.reports_building.domain.services.validation import ModelValidationService
from kin_txt_core.reports_building.domain.services.statistical_report.statistical_strategy import StatisticalStrategy
from kin_txt_core.reports_building.domain.services.word_cloud.wc_token_classification_strategy import (
    BuildWordCloudTokenClassificationStrategy
)
from kin_txt_core.reports_building.domain.services.word_cloud.wc_strategy import WordCloudStrategy
from kin_txt_core.reports_building.constants import REPORTS_BUILDER_EXCHANGE
from kin_txt_core.reports_building.settings import Settings


class SubscriberResource(resources.Resource):
    def init(
        self,
        client: RabbitClient,
        additional_subscriptions: Iterable[Subscription] | None = None,
    ) -> AbstractEventSubscriber:
        subscriber = RabbitSubscriber(client=client, settings=Settings())

        from kin_txt_core.reports_building.events.handlers import (
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

    statistical_report_service: providers.Factory[StatisticalStrategy] = providers.Factory(
        StatisticalStrategy,
        events_producer=messaging.producer,
        statistics_service=services.statistics_service,
        model_types_service=services.model_types_service,
        predictor_factory=predictor_factory,
        datasource_factory=factories.datasource_factory,
    )

    word_cloud_service: providers.Factory[WordCloudStrategy] = providers.Factory(
        WordCloudStrategy,
        events_producer=messaging.producer,
        statistics_service=services.statistics_service,
        model_types_service=services.model_types_service,
        predictor_factory=predictor_factory,
        datasource_factory=factories.datasource_factory,
    )

    word_cloud_token_classification_service: providers.Factory[BuildWordCloudTokenClassificationStrategy] = providers.Factory(
        BuildWordCloudTokenClassificationStrategy,
        events_producer=messaging.producer,
        statistics_service=services.statistics_service,
        model_types_service=services.model_types_service,
        predictor_factory=predictor_factory,
        datasource_factory=factories.datasource_factory,
    )

    generate_request_handler_service: providers.Singleton[GenerateRequestHandlerService] = providers.Singleton(
        GenerateRequestHandlerService,
        predictor_factory=predictor_factory,
        model_types_service=services.model_types_service,
        statistical_reports_service=statistical_report_service,
        word_cloud_service=word_cloud_service,
        word_cloud_token_classification_service=word_cloud_token_classification_service
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
