from smtools import logger
from smtools.ext.core.builder import TrainingBuilder


class Training:
    def __init__(self) -> None:
        self._builder = None
        self._config = None

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, config) -> None:
        self._config = config

    @property
    def builder(self) -> TrainingBuilder:
        return self._builder

    @builder.setter
    def builder(self, builder: TrainingBuilder) -> None:
        """
        The Director works with any builder instance that the client code passes
        to it. This way, the client code may alter the final type of the newly
        assembled product.
        """
        self._builder = builder

    """
    The Director can construct several product variations using the same
    building steps.
    """

    def build_minimal_viable_pipeline(self) -> None:
        logger.info("build minimal viable pipeline")

        logger.info("produce paramters")
        self.builder.produce_paramters(self._config.parameters)

        logger.info("produce pre_process_data")
        self.builder.produce_pre_process_data(self._config)

    def build_full_featured_pipeline(self) -> None:
        self.builder.produce_pre_process_data()
        self.builder.produce_train()
        self.builder.produce_evaluation()
        self.builder.produce_condition()
