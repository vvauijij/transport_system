import uuid

from worker import Courier
from store import Store


class Client:
    __slots__ = ['_client_id',
                 '_sent_orders_id',
                 '_received_orders',
                 '_x',
                 '_y']

    def __init__(self, client_id: uuid, x: int, y: int):
        self._client_id = client_id
        self._x = x
        self._y = y
        self._sent_orders_id = set()
        self._received_orders = dict()  # order_id - order

        print('client: {0} registered'.format(client_id))

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y

    def make_order(self, items: dict, store: Store) -> uuid:
        print('client: {0} made order in store: {1}'.format(self._client_id, store.store_id))
        order_id = store.take_order(self._client_id, self._x, self._y, items)
        self._sent_orders_id.add(order_id)
        return order_id

    def take_order(self, order_id: uuid, courier: Courier) -> bool:
        if order_id in self._sent_orders_id and courier.able_to_pass(order_id):
            self._sent_orders_id.remove(order_id)
            self._received_orders[order_id] = courier.pass_order()

            print('client: {0} took order: {1} from courier: {2}'.format(self._client_id,
                                                                         order_id,
                                                                         courier.worker_id))

            return True

        else:
            print('client: {0} didnt take order: {1} from courier: {2}'.format(self._client_id,
                                                                               order_id,
                                                                               courier.worker_id))

            return False
