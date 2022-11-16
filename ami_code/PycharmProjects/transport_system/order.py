from dataclasses import dataclass

import enum
import time
import uuid


@dataclass
class Item:
    __slots__ = ['_name',
                 '_price',
                 '_at_store_id',
                 '_at_provider_id',
                 '_provider_id']
    _name: str
    _price: int

    _at_store_id: uuid
    _at_provider_id: uuid
    _provider_id: uuid

    @property
    def name(self) -> str:
        return self._name

    @property
    def price(self) -> int:
        return self._price

    @property
    def at_provider_id(self) -> uuid:
        return self._at_provider_id

    @property
    def at_store_id(self) -> uuid:
        return self._at_store_id

    @property
    def provider_id(self) -> uuid:
        return self._provider_id


class OrderStatus(enum.Enum):
    NEW = 1
    READY_TO_ASSEMBLE = 2
    ASSEMBLE = 3
    DELIVER = 4
    COMPLETE = 5


@dataclass
class Order:
    __slots__ = ['_client_id',
                 '_order_id',
                 '_order_status',
                 '_creation_time',
                 '_estimated_delivery_time',
                 '_x',
                 '_y',
                 '_items',
                 '_storekeeper_id',
                 '_courier_id']

    _client_id: uuid
    _order_id: uuid
    _order_status: OrderStatus
    _creation_time: float
    _estimated_delivery_time: float
    _x: int
    _y: int
    _items: dict
    _storekeeper_id: uuid
    _courier_id: uuid

    @property
    def client_id(self) -> uuid:
        return self._client_id

    @property
    def order_id(self) -> uuid:
        return self._order_id

    @property
    def order_status(self) -> OrderStatus:
        return self._order_status

    @property
    def creation_time(self) -> float:
        return self._creation_time

    @property
    def estimated_delivery_time(self) -> float:
        return self._estimated_delivery_time

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y

    @property
    def items(self) -> dict:
        return self._items

    @property
    def storekeeper_id(self) -> uuid:
        return self._storekeeper_id

    @property
    def courier_id(self) -> uuid:
        return self._courier_id

    @order_status.setter
    def order_status(self, value: OrderStatus):
        self._order_status = value

    @creation_time.setter
    def creation_time(self, value: float) -> None:
        self._creation_time = value

    @estimated_delivery_time.setter
    def estimated_delivery_time(self, value: float) -> None:
        self._estimated_delivery_time = value

    @storekeeper_id.setter
    def storekeeper_id(self, value: uuid) -> None:
        self._storekeeper_id = value

    @courier_id.setter
    def courier_id(self, value: uuid) -> None:
        self._courier_id = value

    def __getitem__(self, item_id: str) -> int:
        if item_id in self._items:
            return self._items[item_id]
        else:
            return 0

    def __setitem__(self, item_id: str, amount: int) -> None:
        self._items[item_id] = amount

    def check_time(self) -> bool:
        return self._estimated_delivery_time <= time.time()
