import os
import requests
import sqlite3
url = "http://127.0.0.1:8000/api/"


# # response = requests.post(url, json=payload)
# response = requests.get(url)
# print(response.json())
import unittest

class TestStringMethods(unittest.TestCase):
    def test_acreate_user(self):
        payload = {
            "user_id": 1,
            "user_name": "Fahim",
            "balance": 100
        }
        response = requests.post(url + "users", json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {**payload})

    def test_bno_stations(self):
        response = requests.get(url + "stations")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"stations": []})

    def test_create_train(self):
        payload = {
            "train_id": 1,
            "train_name": "Mahanagar 123",
            "capacity": 200,
            "stops": [
                {
                "station_id": 1,
                "arrival_time": None,
                "departure_time": "07:00",
                "fare": 0
                },
                {
                "station_id": 3,
                "arrival_time": "07:45",
                "departure_time": "07:50",
                "fare": 20
                },
                {
                "station_id": 4,
                "arrival_time": "08:30",
                "departure_time": None,
                "fare": 30
                }
            ]
        }

        response_expected = {
            "train_id": 1,
            "train_name": "Mahanagar 123",
            "capacity": 200,
            "service_start": "07:00",
            "service_ends": "08:30",
            "num_stations": 3
        }

        response = requests.post(url + "trains", json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {**response_expected})

    def test_dcreate_station(self):
        payload = {
            "station_id": 1,
            "station_name": "Dhaka",
            "longitude": 90.4,
            "latitude": 23.7
        }
        response = requests.post(url + "stations", json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {**payload})

    def test_eget_stations(self):
        payload = {
            "stations": [
                {
                    "station_id": 1,
                    "station_name": "Dhaka",
                    "longitude": 90.4,
                    "latitude": 23.7
                }
            ]
        }
        response = requests.get(url + "stations")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), payload)

    def test_fget_trains_from_station(self):
        payload = {
            "station_id": 1,
            "trains": [
                {
                    "train_id": 1,
                    "arrival_time": None,
                    "departure_time": "07:00",
                }
            ]
        }
        response = requests.get(url + "stations/1/trains")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), payload)

    def test_hcreate_station(self):
        payload = {
            "station_id": 3,
            "station_name": "ChittaGong",
            "longitude": 95.4,
            "latitude": 26.7
        }
        response = requests.post(url + "stations", json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {**payload})

    def test_iget_stations(self):
        payload = {
            "stations": [
                {
                    "station_id": 1,
                    "station_name": "Dhaka",
                    "longitude": 90.4,
                    "latitude": 23.7
                },
                {
                    "station_id": 3,
                    "station_name": "ChittaGong",
                    "longitude": 95.4,
                    "latitude": 26.7
                }
            ]
        }
        response = requests.get(url + "stations")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), payload)

    def test_jget_trains_from_station_doesnt_exist(self):
        payload = {
            "message": "station with id: 4 was not found"
        }
        response = requests.get(url + "stations/4/trains")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), payload)
    
    def test_kcreate_station(self):
        payload = {
            "station_id": 9,
            "station_name": "Sylhet",
            "longitude": 99.4,
            "latitude": 29.7
        }
        response = requests.post(url + "stations", json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {**payload})

    def test_lget_trains_from_station_with_no_stops(self):
        payload = {
            "station_id": 9,
            "trains": []
        }
        response = requests.get(url + "stations/9/trains")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), payload)

    def test_mget_wallet_not_found(self):
        payload = {
            "message": "wallet with id: 9 was not found"
        }
        response = requests.get(url + "wallets/9")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), payload)

    def test_mget_wallet(self):
        payload = {
            "wallet_id": 1,
            "balance": 100,
            "wallet_user": {
                "user_id": 1,
                "user_name": "Fahim"
            }
        }
        response = requests.get(url + "wallets/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), payload)
    
    def test_nupdate_wallet(self):
        payload = {
            "recharge": 100
        }
        response_payload = {
            "wallet_id": 1,
            "balance": 200,
            "wallet_user": {
                "user_id": 1,
                "user_name": "Fahim"
            }
        }
        response = requests.put(url + "wallets/1", payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), response_payload)

if __name__ == '__main__':

    unittest.main()
    db = sqlite3.connect(os.environ.get('DATABASE_URL'), check_same_thread=False)
    cursor = db.cursor()
    cursor.execute('DROP TABLE IF EXISTS users')
    cursor.execute('DROP TABLE IF EXISTS stations')
    cursor.execute('DROP TABLE IF EXISTS trains')
    cursor.execute('DROP TABLE IF EXISTS train_stops')

    db.commit()
    
    