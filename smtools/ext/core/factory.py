from sagemaker.sklearn.processing import SKLearnProcessor

from smtools.ext.core.singleton import ml_platform


class ObjectFactory:
    def __init__(self):
        self._builders = {}

    @property
    def builders(self):
        return self._builders

    def register_builder(self, key, builder):
        self._builders[key] = builder

    def create(self, key, **kwargs):
        builder = self._builders.get(key)
        if not builder:
            raise ValueError(key)
        return builder(**kwargs)


class SageMakerProcessorFactory(ObjectFactory):
    def get_or_create(self, service, **kwargs):
        return self.create(service, **kwargs)


class SKLearnProcessorBuilder:
    def __init__(self) -> None:
        self._instance = None

    def __call__(
        self, framework_version, instance_type, instance_count, base_job_name, **_ignored
    ) -> SKLearnProcessor:
        if not self._instance:
            self._instance = SKLearnProcessor(
                framework_version=framework_version,
                instance_type=instance_type,
                instance_count=instance_count,
                base_job_name=base_job_name,
                role=ml_platform.role,
                sagemaker_session=ml_platform.session,
            )
        return self._instance


sagemaker_processor_factory = SageMakerProcessorFactory()
sagemaker_processor_factory.register_builder("SKLearnProcessor", SKLearnProcessorBuilder())
