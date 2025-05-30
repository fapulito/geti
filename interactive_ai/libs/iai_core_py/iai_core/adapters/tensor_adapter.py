"""This module contains the implementation of the TensorAdapter"""

import numpy as np

# Copyright (C) 2022-2025 Intel Corporation
# LIMITED EDGE SOFTWARE DISTRIBUTION LICENSE
from iai_core.adapters.binary_interpreters import NumpyBinaryInterpreter
from iai_core.entities.interfaces.tensor_adapter_interface import TensorAdapterInterface
from iai_core.repos.storage.binary_repos import TensorBinaryRepo


class TensorAdapter(TensorAdapterInterface):
    """
    The TensorAdapter is an adapter intended to lazily fetch the stored numpy data from a given repo.
    Holds metadata of the Tensor, such as width and height,
    so it doesn't need to consult the binary data for this information.
    """

    def __init__(self, data_source: TensorBinaryRepo, binary_filename: str, shape: tuple[int, ...]) -> None:
        super().__init__(repo_adapter=data_source, binary_filename=binary_filename)
        self.__shape = shape

    def __eq__(self, other: object):
        if not isinstance(other, TensorAdapter):
            return False
        return self.binary_filename == other.binary_filename and self.shape == other.shape

    @property
    def shape(self) -> tuple[int, ...]:
        return self.__shape

    @property
    def numpy(self) -> np.ndarray:
        if self.repo_adapter is None or self.binary_filename is None:
            raise ValueError(
                "This task configuration adapter has no filename, nor does it have a data source to fetch the data"
            )
        return self.repo_adapter.get_by_filename(
            filename=self.binary_filename, binary_interpreter=NumpyBinaryInterpreter()
        )

    @property
    def size_on_storage(self) -> int:
        """
        Return the consumed storage (in bytes) of the entity
        """
        return self.repo_adapter.get_object_size(filename=self.binary_filename)
