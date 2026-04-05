import requests

mock_data = [
    {"asin":"B001","seller_name":"Amazon","price":1000,"is_buybox":True,"delivery_days":1},
    {"asin":"B001","seller_name":"SellerX","price":950,"is_buybox":False,"delivery_days":5},
    {"asin":"B001","seller_name":"SellerY","price":970,"is_buybox":False,"delivery_days":3}
]

for item in mock_data:
    res = requests.post("http://127.0.0.1:8000/add_seller", json=item)
    print(res.json())