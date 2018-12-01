import trio
from abc import ABCMeta, abstractmethod
from typing import (
    List, Tuple, Union, Any, Optional, Generic, TypeVar,
    AsyncIterator
)

T = TypeVar('T')

class Clock(metaclass=ABCMeta):
    @abstractmethod
    def start_clock(self) -> None: ...
    @abstractmethod
    def current_time(self) -> float: ...
    @abstractmethod
    def deadline_to_sleep_time(self, deadline: float) -> float: ...

class Instrument(metaclass=ABCMeta):
    def before_run(self) -> None: ...
    def after_run(self) -> None: ...
    def task_spawned(self, task: trio.hazmat.Task) -> None: ...
    def task_scheduled(self, task: trio.hazmat.Task) -> None: ...
    def before_task_step(self, task: trio.hazmat.Task) -> None: ...
    def after_task_step(self, task: trio.hazmat.Task) -> None: ...
    def task_exited(self, task: trio.hazmat.Task) -> None: ...
    def before_io_wait(self, timeout: float) -> None: ...
    def after_io_wait(self, timeout: float) -> None: ...

class HostnameResolver(metaclass=ABCMeta):
    @abstractmethod
    async def getaddrinfo(
        self,
        host: Union[bytearray, bytes, str],
        port: Union[str, int, None],
        family: int = ...,
        type: int = ...,
        proto: int = ...,
        flags: int = ...
    ) -> List[Tuple[int, int, int, str, Tuple[Any, ...]]]: ...

    @abstractmethod
    async def getnameinfo(
        self, sockaddr: tuple, flags: int
    ) -> Tuple[str, int]: ...

class SocketFactory(metaclass=ABCMeta):
    @abstractmethod
    def socket(
        self,
        family: Optional[int] = None,
        type: Optional[int] = None,
        proto: Optional[int] = None,
    ) -> trio.socket.SocketType: ...

class AsyncResource(metaclass=ABCMeta):
    @abstractmethod
    async def aclose(self): ...
    async def __aenter__(self: T) -> T: ...
    async def __aexit__(self, *exc) -> bool: ...

class SendStream(AsyncResource):
    @abstractmethod
    async def send_all(
        self, data: Union[bytes, bytearray, memoryview]
    ) -> None: ...

    @abstractmethod
    async def wait_send_all_might_not_block(self) -> None: ...

class ReceiveStream(AsyncResource):
    @abstractmethod
    async def receive_some(self, max_bytes: int) -> Union[bytes, bytearray]: ...

class Stream(SendStream, ReceiveStream, metaclass=ABCMeta): pass

class HalfCloseableStream(Stream):
    @abstractmethod
    async def send_eof(self) -> None: ...

_SomeResource = TypeVar('_SomeResource', bound=AsyncResource)
class Listener(AsyncResource, Generic[_SomeResource]):
    @abstractmethod
    async def accept(self) -> _SomeResource: ...

_T1 = TypeVar('_T1')

T_co = TypeVar('T_co', covariant=True)
T_contra = TypeVar('T_contra', contravariant=True)

class SendChannel(AsyncResource, Generic[T_contra]):
    @abstractmethod
    def send_nowait(self, value: T_contra) -> None: ...
    @abstractmethod
    async def send(self, value: T_contra) -> None: ...
    @abstractmethod
    def clone(self: _T1) -> _T1: ...

class ReceiveChannel(AsyncResource, Generic[T_co]):
    @abstractmethod
    def receive_nowait(self) -> T_co: ...
    @abstractmethod
    async def receive(self) -> T_co: ...
    @abstractmethod
    def clone(self: _T1) -> _T1: ...

    def __aiter__(self) -> AsyncIterator[T_co]: ...
    async def __anext__(self) -> T_co: ...

