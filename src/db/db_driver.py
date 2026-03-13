"""
abstract class to define the interface of each supported low-level database implementation

"""

import abc
import logging

from service.logger import setup_logging

setup_logging()
log = logging.getLogger(__name__)

class DBDriver(metaclass=abc.ABCMeta):



    @abc.abstractmethod
    def create_engine(self):
        raise NotImplementedError


    @abc.abstractmethod
    def create_session(self):
        raise NotImplementedError

