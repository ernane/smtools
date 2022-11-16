from abc import ABC, abstractmethod


class AbstractTraining(ABC):
    """
    The Builder interface specifies methods for creating the different parts of
    the SageMaker Pipeline of Model Training objects.
    """

    @property
    @abstractmethod
    def pipeline(self) -> None:
        pass

    @abstractmethod
    def produce_paramters(self) -> None:
        """workflow Parameters"""
        pass

    @abstractmethod
    def produce_pre_process_data(self) -> None:
        """Feature Engineering"""
        pass

    @abstractmethod
    def produce_train(self) -> None:
        """Model Training"""
        pass

    @abstractmethod
    def produce_evaluation(self) -> None:
        """Model Evaluation"""
        pass

    @abstractmethod
    def produce_condition(self) -> None:
        """
        Model Accuracy

        if metric_threshold
            - Model Create
            - Model Package
        else
            - Execution Failed
        """
        pass
