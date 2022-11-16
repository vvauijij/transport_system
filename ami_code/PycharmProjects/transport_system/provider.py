from collections import defaultdict
from order import Item

import uuid


class Provider:
    __slots__ = ['_provider_id',
                 '_items_at_provider_id',
                 '_items_unique',
                 '_items_amount']

    def __init__(self, provider_id: uuid):
        self._provider_id = provider_id

        self._items_at_provider_id = defaultdict(uuid.UUID)  # at_store_id - at_provider_id
        self._items_unique = defaultdict(Item)  # at_provider_id - item
        self._items_amount = defaultdict(int)  # at_provider_id - item amount

        print('provider {0} registered'.format(provider_id))

    @property
    def provider_id(self) -> uuid:
        return self._provider_id

    def add_item(self, item: Item, amount: int) -> None:
        if item.at_provider_id not in self._items_unique:
            self._items_at_provider_id[item.at_store_id] = item.at_provider_id

            self._items_unique[item.at_provider_id] = item
            self._items_amount[item.at_provider_id] = amount
        else:
            self._items_amount[item.at_provider_id] += amount

        print('item: {0}, amount: {1} added to provider: {2}'.format(item.name, amount, self.provider_id))

    def _send_item(self, at_provider_id: uuid, amount: int) -> int:
        if at_provider_id in self._items_amount:
            send_amount = min(amount, self._items_amount[at_provider_id])
            self._items_amount[at_provider_id] -= send_amount

            print('item: {0}, amount: {1} sent by provider: {2}'.format(
                self._items_unique[at_provider_id].name,
                send_amount,
                self.provider_id))

            return send_amount
        else:

            print('item: {0}, amount: {1} sent by provider: {2}'.format(
                self._items_unique[at_provider_id].name,
                0,
                self.provider_id))

            return 0

    def is_possible_to_process_request(self, request: dict) -> bool:
        for [at_store_id, amount] in request.items():
            at_provider_id = self._items_at_provider_id[at_store_id]

            if at_provider_id not in self._items_amount or amount > self._items_amount[at_provider_id]:
                print('request cant be fully processed by provider {0}: not enough items'.format(self.provider_id))

                return False

        print('request can be fully processed by provider {0}'.format(self.provider_id))

        return True

    def process_request(self, request: dict) -> dict:
        for [at_store_id, amount] in request.items():
            at_provider_id = self._items_at_provider_id[at_store_id]
            request[at_store_id] = self._send_item(at_provider_id, amount)

        return request

    def show_items(self):
        print('provider: {0} items:'.format(self._provider_id))
        for [at_provider_id, amount] in self._items_amount.items():
            print('{0}: {1}'.format(self._items_unique[at_provider_id].name, amount))
