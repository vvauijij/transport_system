from collections import defaultdict
from math import hypot
from abc import abstractmethod, ABC

import enum
import time
import uuid

from order import Order, OrderStatus

ASSEMBLE_TIME = 0.05  # set to 45
LEAVE_TIME = 0.05  # set to 60
DELIVERY_CONSTANT = 0.03  # set to 30
PASS_TIME = 0.5  # set to 60


class Worker(ABC):
    class WorkerStatus(enum.Enum):
        FREE = 1
        BUSY = 2
        NOT_AVAILABLE = 3

    __slots__ = ['_worker_id',
                 '_worker_status',
                 '_work_finish_time',
                 '_shift_finish_time'
                 '_order',
                 '_balance']

    def __init__(self, worker_id: uuid) -> None:
        self._worker_id = worker_id
        self._worker_status = Worker.WorkerStatus.FREE
        self._work_finish_time = time.time() - 1
        self._shift_finish_time = defaultdict(float)  # worker may be registered at more than one store
        self._order = None
        self._balance = 0  # worker is paid on a piecework basis

    @abstractmethod
    def get_order(self, order: Order, store) -> None:
        pass

    def get_shift(self, shift: float, store) -> None:
        self._shift_finish_time[store.store_id] = time.time() + shift
        store.add_worker(self)

        print('worker: {0} got shift: {1} at store: {2}'.format(self._worker_id, shift, store.store_id))

    @property
    def worker_id(self) -> uuid.UUID:
        return self._worker_id

    def get_worker_status(self, store) -> WorkerStatus:
        if time.time() > self._shift_finish_time[store.store_id]:
            self._worker_status = Worker.WorkerStatus.NOT_AVAILABLE
            return Worker.WorkerStatus.NOT_AVAILABLE
        elif time.time() > self._work_finish_time:
            self._worker_status = Worker.WorkerStatus.FREE
            return Worker.WorkerStatus.FREE
        else:
            self._worker_status = Worker.WorkerStatus.BUSY
            return Worker.WorkerStatus.BUSY

    def set_worker_status(self, status: WorkerStatus) -> None:
        self._worker_status = status

    @property
    def work_finish_time(self) -> float:
        return self._work_finish_time

    @work_finish_time.setter
    def work_finish_time(self, value: float) -> None:
        self._work_finish_time = value

    @property
    def shift_finish_time(self, store_id):
        return self._shift_finish_time[store_id]

    @shift_finish_time.setter
    def shift_finish_time(self, value: float, store_id) -> None:
        self._shift_finish_time[store_id] = value

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value: int):
        self._balance += value
        print('worker: {0} balance updated: {1}'.format(self.worker_id, self._balance))


class Courier(Worker):
    def __init__(self, worker_id: uuid) -> None:
        super().__init__(worker_id)
        print('courier: {0} registered'.format(worker_id))

    def get_order(self, order: Order, store) -> float:
        if order.order_status == OrderStatus.ASSEMBLE:
            print('courier: {0} got order: {1}'.format(self.worker_id, order.order_id))
            self._worker_status = Worker.WorkerStatus.BUSY
            order.order_status = OrderStatus.DELIVER
            order.courier_id = self.worker_id
            self._order = order

            road_time = hypot((order.x - store.x), (order.y - store.y)) * DELIVERY_CONSTANT
            delivery_time = LEAVE_TIME + road_time + PASS_TIME
            order._estimated_delivery_time = delivery_time
            self._work_finish_time = time.time() + delivery_time + road_time
            print('waiting for delivery...\n')
            time.sleep(delivery_time)
            return delivery_time + road_time
        else:
            print('courier: {0} didnt get order: {1}'.format(self.worker_id, order.order_id))
            return 0

    def able_to_pass(self, order_id: uuid) -> bool:
        if self._order and self._order.order_id == order_id and self._order.check_time():
            print('courier: {0} can pass order: {1}'.format(self.worker_id, order_id))
            return True
        else:
            print('courier: {0} cant pass order: {1}'.format(self.worker_id, order_id))
            return False

    def pass_order(self) -> Order:
        order = self._order
        order.order_status = OrderStatus.DELIVER
        self._order = None
        self._worker_status = Worker.WorkerStatus.FREE
        print('courier: {0} passed order: {1}'.format(self.worker_id, order.order_id))
        return order


class Storekeeper(Worker):
    def __init__(self, worker_id: uuid) -> None:
        super().__init__(worker_id)
        print('storekeeper: {0} registered'.format(worker_id))

    def get_order(self, order: Order, store) -> float:
        if order.order_status == OrderStatus.READY_TO_ASSEMBLE:
            self._order = order

            estimated_assemble_time = 0
            for [item_name, amount] in order.items.items():
                store.items_amount[store.items_at_store_id[item_name]] -= amount
                estimated_assemble_time += amount * ASSEMBLE_TIME

            self._work_finish_time = time.time() + estimated_assemble_time
            order.storekeeper_id = self.worker_id
            order.estimated_delivery_time += estimated_assemble_time
            print('storekeeper: {0} got order: {1}'.format(self.worker_id, order.order_id))
            return estimated_assemble_time
        else:
            print('storekeeper: {0} didnt get order: {1}: wrong status'.format(self.worker_id, order.order_id))
            return 0

    def finish_assembly(self):
        order = self._order
        self._order = None
        self._work_finish_time = time.time()
        order.order_status = OrderStatus.ASSEMBLE
        print('storekeeper: {0} assemble order: {1}'.format(self.worker_id, order.order_id))
        return order
