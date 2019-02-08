# Copyright 2018 eShares, Inc. dba Carta, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

from abc import ABCMeta, abstractmethod
from typing import Any, Dict


class AbstractBucketer(metaclass=ABCMeta):
    @abstractmethod
    def check(self, **checks) -> bool:
        pass

    @staticmethod
    @abstractmethod
    def get_type() -> str:
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        return {"type": self.get_type()}

    @classmethod
    @abstractmethod
    def from_dict(cls, fields: Dict[str, Any]) -> "AbstractBucketer":
        pass
