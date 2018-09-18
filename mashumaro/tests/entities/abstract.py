from abc import abstractmethod
from collections.abc import *


class AbstractContainer(Container):
    @abstractmethod
    def foo(self):
        pass


class AbstractHashable(Hashable):
    @abstractmethod
    def foo(self):
        pass


class AbstractIterable(Iterable):
    @abstractmethod
    def foo(self):
        pass


class AbstractIterator(Iterator):
    @abstractmethod
    def foo(self):
        pass


class AbstractReversible(Reversible):
    @abstractmethod
    def foo(self):
        pass


class AbstractGenerator(Generator):
    @abstractmethod
    def foo(self):
        pass


class AbstractSized(Sized):
    @abstractmethod
    def foo(self):
        pass


class AbstractCallable(Callable):
    @abstractmethod
    def foo(self):
        pass


class AbstractCollection(Collection):
    @abstractmethod
    def foo(self):
        pass


class AbstractSequence(Sequence):
    @abstractmethod
    def foo(self):
        pass


class AbstractMutableSequence(MutableSequence):
    @abstractmethod
    def foo(self):
        pass


class AbstractByteString(ByteString):
    @abstractmethod
    def foo(self):
        pass


class AbstractSet(Set):
    @abstractmethod
    def foo(self):
        pass


class AbstractMutableSet(MutableSet):
    @abstractmethod
    def foo(self):
        pass


class AbstractMapping(Mapping):
    @abstractmethod
    def foo(self):
        pass


class AbstractMutableMapping(MutableMapping):
    @abstractmethod
    def foo(self):
        pass


class AbstractMappingView(MappingView):
    @abstractmethod
    def foo(self):
        pass


class AbstractItemsView(ItemsView):
    @abstractmethod
    def foo(self):
        pass


class AbstractKeysView(KeysView):
    @abstractmethod
    def foo(self):
        pass


class AbstractAwaitable(Awaitable):
    @abstractmethod
    def foo(self):
        pass


class AbstractCoroutine(Coroutine):
    @abstractmethod
    def foo(self):
        pass


class AbstractAsyncIterable(AsyncIterable):
    @abstractmethod
    def foo(self):
        pass


class AbstractAsyncIterator(AsyncIterator):
    @abstractmethod
    def foo(self):
        pass


class AbstractAsyncGenerator(AsyncGenerator):
    @abstractmethod
    def foo(self):
        pass
