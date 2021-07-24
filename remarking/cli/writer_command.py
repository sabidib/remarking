import typing as T
from abc import ABCMeta, abstractmethod
from typing import Callable, List, TypeVar

from remarking import models
from remarking.cli import writer as writer_

FC = TypeVar("FC")
ClickOption = Callable[[FC], FC]


class WriterCommand(metaclass=ABCMeta):
    """ Base class for defining writer commands.

        Writer commands are subcommands instructing remarking how to output the results
        of extractors.

        For example, :class:`JSONWriterCommand` adds the json subcommand to ``remarking run``
        and ``remarking persist``.

        Placing a concrete implementation of this class in the ``remarking.cli.commands`` package
        will ensure it is automatically picked up by remarking.
    """

    @abstractmethod
    def name(self) -> str:
        """ Return the name of the command as referenced on the command line. """

    @abstractmethod
    def options(self) -> List[ClickOption]:
        """ Return a list of click options to use for the command.

        The list can be constructed from the return value of :func:`click.option`.

        These options will be added to the default options for the run or persist command.
        """

    @abstractmethod
    def long_description(self) -> str:
        """ The long description for your command. Shown when running ``--help`` """

    @abstractmethod
    def short_description(self) -> str:
        """ The short description of your command. """

    @abstractmethod
    def writer(self,
               documents: List[models.Document],
               highlights: List[models.Highlight],
               **kwargs: T.Any) -> writer_.Writer:
        """ Parse options and return a configured instance of a concrete :class:`Writer` class.


        :param documents: The documents that were processed by extractors.
        :param highlights: The highlights resulting from the extractors.
        :param kwargs: options specified in the :meth:`options` method are available here.

        :return: Return an instance of the writer implementation for your command.
        """
