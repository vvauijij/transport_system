from collections import defaultdict
import time
import uuid

from order import Item, Order, OrderStatus
from provider import Provider
from worker import Worker, Courier, Storekeeper


class Store:
    __slots__ = ['_store_id',
                 '_items_at_store_id',
                 '_items_unique',
                 '_items_amount',
                 '_providers',
                 '_orders',
                 '_new_orders',
                 '_assemble_orders',
                 '_deliver_orders',
                 '_complete_orders',
                 '_couriers',
                 '_storekeepers',
                 '_x',
                 '_y']

    def __init__(self, store_id: uuid, x: int, y: int):
        self._store_id = store_id
        self._x = x
        self._y = y
        self._items_at_store_id = dict()  # item name - at_store_id
        self._items_unique = dict()  # at_store_id - item
        self._items_amount = defaultdict(int)  # at_store_id - item amount

        self._providers = dict()  # provider_id - provider

        self._orders = dict()
        self._new_orders = set()
        self._assemble_orders = set()
        self._deliver_orders = set()
        self._complete_orders = set()

        self._couriers = dict()  # worker_id - worker
        self._storekeepers = dict()  # worker_id - worker

        print('store: {0} registered'.format(store_id))

    @property
    def store_id(self) -> uuid:
        return self._store_id

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y

    @property
    def items_amount(self) -> dict:
        return self._items_amount

    @property
    def items_at_store_id(self) -> dict:
        return self._items_at_store_id

    def add_category(self, item: Item) -> None:
        if item.at_store_id not in self._items_unique:
            self._items_unique[item.at_store_id] = item
            self._items_amount[item.at_store_id] = 0
            self._items_at_store_id[item.name] = item.at_store_id

            print('store: {0} now cells {1}'.format(self.store_id, item.name))

    def add_provider(self, provider: Provider) -> None:
        self._providers[provider.provider_id] = provider
        print('provider: {0} now supports store: {1}'.format(provider.provider_id, self.store_id))

    def update_stocks(self, request: dict) -> None:
        for [at_store_id, amount] in request.items():
            self._items_amount[at_store_id] += amount

            print('store: {0} now has item: {1} amount: {2}'.format(self.store_id,
                                                                    self._items_unique[at_store_id].name,
                                                                    self._items_amount[at_store_id]))

    def send_request(self, provider: Provider, request: dict) -> None:
        print('request sent from store: {0} to provider: {1}'.format(self.store_id, provider.provider_id))

        provider.process_request(request)
        self.update_stocks(request)

    def take_order(self, client_id: uuid, x: int, y: int, items: dict) -> uuid:
        order_id = uuid.uuid1()

        order = Order(_client_id=client_id,
                      _order_id=order_id,
                      _order_status=OrderStatus.NEW,
                      _creation_time=time.time(),
                      _estimated_delivery_time=time.time(),
                      _x=x,
                      _y=y,
                      _items=items,
                      _courier_id='',
                      _storekeeper_id='')

        self._orders[order_id] = order
        self._new_orders.add(order_id)

        self.process_order(order_id)

        return order_id

    def show_items(self):
        print('store: {0} items:'.format(self._store_id))
        for [at_store_id, amount] in self._items_amount.items():
            print('{0}: {1}'.format(self._items_unique[at_store_id].name, amount))

    def process_order(self, order_id: uuid):
        if order_id not in self._orders.keys():
            print('order: {0} processing failed: wrong order id'.format(order_id))
            return
        elif self._orders[order_id].order_status == OrderStatus.NEW:
            print('store: {0} is starting to process order: {1}'.format(self._store_id, order_id))
            request = defaultdict()

            for [item_name, item_amount] in self._orders[order_id].items.items():
                available_amount = self._items_amount[self._items_at_store_id[item_name]]
                if available_amount < item_amount:
                    request[self._items_at_store_id[item_name]] = item_amount - available_amount

            stocks_updated = False
            for [provider_id, provider] in self._providers.items():
                if provider.is_possible_to_process_request(request):
                    self.update_stocks(provider.process_request(request))
                    stocks_updated = True
                    break

            if not stocks_updated:
                print(
                    'order: {0} cant be fully processed by store: {1}: not enough items, need to wait'.format(
                        order_id,
                        self.store_id))
                return
            else:
                self._orders[order_id].order_status = OrderStatus.READY_TO_ASSEMBLE
                print('store: {0} stocks updated, order: {1} ready to assemble'.format(self.store_id, order_id))

        if self._orders[order_id].order_status == OrderStatus.READY_TO_ASSEMBLE:
            storekeeper_found = False

            for [storekeeper_id, storekeeper] in self._storekeepers.items():
                if storekeeper.get_worker_status(self) == Worker.WorkerStatus.FREE:
                    storekeeper_found = True
                    self.show_items()
                    self.set_storekeeper(storekeeper_id, order_id)
                    self.show_items()
                    break

            if not storekeeper_found:
                print(
                    'order: {0} cant be fully processed by store: {1}: no storekeepers are free - need to wait'.format(
                        order_id,
                        self.store_id))
                return

        if (self._orders[order_id].order_status == OrderStatus.ASSEMBLE and
                self._orders[order_id].estimated_delivery_time <= time.time()):
            courier_found = False
            for [courier_id, courier] in self._couriers.items():
                if courier.get_worker_status(self) == Worker.WorkerStatus.FREE:
                    courier_found = True
                    self.set_courier(courier_id, order_id)
                    break

            if not courier_found:
                print('order: {0} cant be fully processed by store: {1}: no couriers are free - need to wait'.format(
                    order_id,
                    self.store_id))
                return
        elif (self._orders[order_id].order_status == OrderStatus.ASSEMBLE and
              self._orders[order_id].estimated_delivery_time > time.time()):
            print('order: {0} is not assembled - need to wait'.format(order_id))
            return

        print('order: {0} is fully processed by store: {1}:'.format(order_id, self.store_id))

    def set_courier(self, courier_id: uuid, order_id: uuid):
        self._orders[order_id].courier_id = courier_id
        print('courier: {0} is responsible for delivering order: {1}'.format(courier_id, order_id))
        work_time = self._couriers[courier_id].get_order(self._orders[order_id], self)
        if self._couriers[courier_id].able_to_pass(order_id):
            self._couriers[courier_id].pass_order()
            self._couriers[courier_id].balance += 300 * work_time

    def set_storekeeper(self, storekeeper_id: uuid, order_id: uuid):
        self._orders[order_id].storekeeper_id = storekeeper_id
        print('storekeeper: {0} is responsible for assembling order: {1}'.format(storekeeper_id, order_id))
        work_time = self._storekeepers[storekeeper_id].get_order(self._orders[order_id], self)
        self._storekeepers[storekeeper_id].finish_assembly()
        self._storekeepers[storekeeper_id].balance += 300 * work_time

    def add_worker(self, worker: Worker):
        if isinstance(worker, Courier):
            self._couriers[worker.worker_id] = worker
        else:
            self._storekeepers[worker.worker_id] = worker
        print('worker: {0} now works for store: {1}'.format(worker.worker_id, self.store_id))
