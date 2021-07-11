from get591 import get591
from getnotify import sendLineNotify

items=[
    {
        "location":"中正紀念堂", # optional
        "lat":25.051869,
        "lng":121.525391,
        "dist":5, # km
        "price":10000, # maximum price
        "n_items":6, # first n items
    },
    {
        "location":"劍潭",
        "lat":25.084661,
        "lng":121.522980,
        "dist":5,
        "price":10000,
        "n_items":6,
    },
]
TOKEN='YOUR-TOKEN' # replace your token here
item_list = get591(page=1)
for item in items:
    lat      = item['lat']
    lng      = item['lng']
    dist     = item['dist']
    price    = item['price']
    n_items  = item['n_items']
    location = item['location']

    sendLineNotify(item_list, lat, lng, dist, price, n_items, location, TOKEN)
