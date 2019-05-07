# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""KQL Helper functions."""
import abc
from abc import ABC
from typing import Tuple, Any, Union

import pandas as pd

from ... _version import VERSION

__version__ = VERSION
__author__ = 'Ian Hellen'


class DataProviderBase(ABC):
    """Base class for data providers."""

    def __init__(self, **kwargs):
        """Initialize new instance."""
        self._kwargs = kwargs
        self._loaded = False
        self._connected = False

    @property
    def loaded(self) -> bool:
        """
        Return true if the provider is loaded.

        Returns
        -------
        bool
            True if the provider is loaded.

        Notes
        -----
        This is not relevant for some providers.

        """
        return self._loaded

    @property
    def connected(self) -> bool:
        """
        Return true if at least one connection has been made.

        Returns
        -------
        bool
            True if a successful connection has been made.

        Notes
        -----
        This does not guarantee that the last data source
        connection was successful. It is a best effort to track
        whether the provider has made at least one successful
        authentication.

        """
        return self._loaded

    @abc.abstractmethod
    def connect(self, connection_str: str, **kwargs):
        """
        Connect to data source.

        Parameters
        ----------
        connection_string : str
            Connect to a data source

        """
        return None

    @abc.abstractmethod
    def query(self, query: str) -> Union[pd.DataFrame, Any]:
        """
        Execute query string and return DataFrame of results.

        Parameters
        ----------
        query : str
            The query to execute

        Returns
        -------
        Union[pd.DataFrame, Any]
            A DataFrame (if successfull) or
            the underlying provider result if an error.

        """

    @abc.abstractmethod
    def query_with_results(self, query: str) -> Tuple[pd.DataFrame,
                                                      Any]:
        """
        Execute query string and return DataFrame plus native results.

        Parameters
        ----------
        query : str
            The query to execute

        Returns
        -------
        Tuple[pd.DataFrame,Any]
            A DataFrame and native results.

        """
