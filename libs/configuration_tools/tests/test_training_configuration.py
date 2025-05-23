# Copyright (C) 2022-2025 Intel Corporation
# LIMITED EDGE SOFTWARE DISTRIBUTION LICENSE

import pytest
from geti_types import ID
from pydantic import ValidationError

from geti_configuration_tools.hyperparameters import (
    AugmentationParameters,
    CenterCrop,
    DatasetPreparationParameters,
    EvaluationParameters,
    Hyperparameters,
    TrainingHyperParameters,
)
from geti_configuration_tools.training_configuration import (
    Filtering,
    GlobalDatasetPreparationParameters,
    GlobalParameters,
    SubsetSplit,
    TrainingConfiguration,
)


@pytest.fixture
def ftx_hyperparameters():
    yield Hyperparameters(
        dataset_preparation=DatasetPreparationParameters(
            augmentation=AugmentationParameters(
                center_crop=CenterCrop(ratio=0.6),
            )
        ),
        training=TrainingHyperParameters(
            max_epochs=100,
            early_stopping_epochs=10,
            learning_rate=0.001,
            learning_rate_warmup_epochs=5,
            batch_size=32,
        ),
        evaluation=EvaluationParameters(),
    )


class TestTrainingConfiguration:
    def test_valid_training_configuration(self, ftx_hyperparameters):
        # Create a valid TrainingConfiguration
        training_config = TrainingConfiguration(
            id_=ID("test_training_config"),
            task_id=ID("test_task"),
            global_parameters=GlobalParameters(
                dataset_preparation=GlobalDatasetPreparationParameters(
                    subset_split=SubsetSplit(
                        training=70,
                        validation=20,
                        test=10,
                        auto_selection=True,
                        remixing=False,
                    ),
                    filtering=Filtering(
                        min_annotation_pixels=10,
                        max_annotation_pixels=1000,
                        max_annotation_objects=100,
                    ),
                )
            ),
            hyperparameters=ftx_hyperparameters,
        )

        # Verify the created config properties
        assert training_config.global_parameters.dataset_preparation.subset_split.training == 70
        assert training_config.global_parameters.dataset_preparation.subset_split.validation == 20
        assert training_config.global_parameters.dataset_preparation.subset_split.test == 10
        assert training_config.hyperparameters.training.max_epochs == 100

    def test_invalid_subset_split(self, ftx_hyperparameters):
        # Test that validation fails when subset percentages don't add up to 100
        with pytest.raises(ValidationError) as excinfo:
            TrainingConfiguration(
                id_=ID("test_training_config"),
                global_parameters=GlobalParameters(
                    dataset_preparation=GlobalDatasetPreparationParameters(
                        subset_split=SubsetSplit(
                            training=60,  # Sum is 90, not 100
                            validation=20,
                            test=10,
                            auto_selection=True,
                            remixing=False,
                        ),
                        filtering=Filtering(),
                    )
                ),
                hyperparameters=ftx_hyperparameters,
            )

        assert "Sum of subsets should be equal to 100" in str(excinfo.value)

    def test_invalid_annotation_pixels(self, ftx_hyperparameters):
        # Test validation for annotation pixels
        with pytest.raises(ValidationError):
            TrainingConfiguration(
                id_=ID("test_training_config"),
                global_parameters=GlobalParameters(
                    dataset_preparation=GlobalDatasetPreparationParameters(
                        subset_split=SubsetSplit(),
                        filtering=Filtering(
                            min_annotation_pixels=0,  # Invalid: must be > 0
                        ),
                    )
                ),
                hyperparameters=ftx_hyperparameters,
            )
