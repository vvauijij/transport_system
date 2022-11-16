import time
from collections import defaultdict
import uuid

from order import Item, Order
from provider import Provider
from worker import Courier, Storekeeper
from store import Store
from client import Client

items = {'pen': Item(_name='pen',
                     _price=12,
                     _at_store_id=uuid.uuid1(),
                     _at_provider_id=uuid.uuid1(),
                     _provider_id=None),
         'pencil': Item(_name='pencil',
                        _price=10,
                        _at_store_id=uuid.uuid1(),
                        _at_provider_id=uuid.uuid1(),
                        _provider_id=None),
         'rubber': Item(_name='rubber',
                        _price=7,
                        _at_store_id=uuid.uuid1(),
                        _at_provider_id=uuid.uuid1(),
                        _provider_id=None)}

provider1 = Provider(uuid.uuid1())  # provider1 registered
provider2 = Provider(uuid.uuid1())  # provider2 registered
print('\n')

for [item_name, item] in items.items():
    provider1.add_item(item=item, amount=7)
provider1.show_items()  # provider1 updated stocks
print('\n')

for [item_name, item] in items.items():
    provider2.add_item(item=item, amount=12)
provider2.show_items()  # provider2 updated stocks
print('\n')

courier1 = Courier(uuid.uuid1())  # courier1 registered
courier2 = Courier(uuid.uuid1())  # courier2 registered
storekeeper1 = Storekeeper(uuid.uuid1())  # storekeeper1 registered
print('\n')

store1 = Store(uuid.uuid1(), -10, -10)  # store1 registered
store1.add_provider(provider1)  # store1 add provider1
store1.add_provider(provider2)  # store1 add provider2
print('\n')
store1.add_category(items['pen'])  # store1 add category
store1.add_category(items['pencil'])  # store1 add category
store1.add_category(items['rubber'])  # store1 add category
print('\n')
storekeeper1.get_shift(70, store1)  # storekeeper1 get shift
courier1.get_shift(50, store1)  # courier1 get shift
print('\n')

store2 = Store(uuid.uuid1(), 10, 10)  # store2 registered
store2.add_provider(provider1)  # store2 add provider1
store2.add_provider(provider2)  # store2 add provider2
print('\n')

store2.add_category(items['pen'])  # store2 add category
store2.add_category(items['pencil'])  # store2 add category
print('\n')

storekeeper1.get_shift(100, store2)  # storekeeper1 get shift
courier2.get_shift(30, store2)  # courier2 get shift
print('\n')

client1 = Client(uuid.uuid1(), 10, -10)  # client1 registered
client2 = Client(uuid.uuid1(), -10, 10)  # client1 registered
print('\n')

print('----------------------------------------ORDER1 OPENED----------------------------------------')
order1 = client1.make_order({'pen': 10, 'pencil': 12}, store1)
print('waiting...\n')
time.sleep(1.5)
store1.process_order(order1)
print('----------------------------------------ORDER1 CLOSED----------------------------------------\n\n\n')

print('----------------------------------------ORDER2 OPENED----------------------------------------')
order2 = client2.make_order({'pen': 10, 'pencil': 1}, store2)
print('waiting...\n')
time.sleep(1.5)
store2.process_order(order1)  # trying to process wrong order
store2.process_order(order2)
print('----------------------------------------ORDER2 CLOSED----------------------------------------\n\n\n')

print('----------------------------------------ORDER3 OPENED----------------------------------------')
order3 = client2.make_order({'pen': 7, 'pencil': 1}, store2)
print('waiting...\n')
time.sleep(1.5)
store2.process_order(order3)
print('----------------------------------------ORDER3 CLOSED----------------------------------------\n\n\n')
