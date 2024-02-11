import os
from fastapi import FastAPI, HTTPException, Depends, Response
import json
import heapq

from database import TrainService

from typing import Dict

app = FastAPI()

db = TrainService(os.environ.get('DATABASE_NAME'))

# Purchase Ticket

# Users can use their wallet balance to purchase tickets from stations A to B. The cost is calculated as the sum of
# the fares for each pair of consecutive stations along the route. Upon successful purchase, your API should
# respond with the station in order visited by one or more trains and the remaining wallet balance. If the wallet
# does not have sufficient funds, respond with an error specifying the shortage amount. If it is impossible to
# reach station B from station A within the day or due to a lack of trains, respond with an error specifying that no
# tickets are available.
# Note: The user may want to change the train at a particular station for a cheaper trip. Partial scoring will be
# awarded if your API fails to find an optimal route. You can assume that the start and destination stations will
# always differ, and the user must complete the trip within the current day.
# Request Specification
# URL: /api/tickets
# Method: POST
# Request model:

# {
# "wallet_id": int, # user's wallet id (same as user id)
# "time_after": string, # time (24 hours hh:mm) after which user
# wants to purchase a ticket
# "station_from": int, # station_id for the starting station
# "station_to": int # station_id for the destination station
# }

# Successful Response
# Upon successful operation, your API must return a 201 status code with the generated ticket ID, remaining
# balance, wallet ID, and a list of all stations in order of visits. You should also include each station's train ID and
# arrival and departure schedules in the output object. Departure time should follow the same time format as in
# the input model. For the first station, the arrival time should be null, and for the last station, the departure
# time should be null.
# Response status: 201 - Created
# Response model

# {
# "ticket_id": int, # generate a unique integer ticket
# ID
# "wallet_id": int, # user's wallet id (same as user
# id)
# "balance": integer, # remaining balance
# "stations": [
# {
# "station_id": integer, # station's numeric id

# "train_id": integer, # train's id user is riding
# "arrival_time": string, # arrival time
# "departure_time": string # departure time
# },
# ...
# ]
# }

# Failed Response
# Insufficient balance
# If the wallet has insufficient balance for purchasing the ticket, respond with HTTP 402 - Payment Required and
# a message showing the shortage amount.
# Response status: 402 - Payment Required
# Response model

# {
# "message": "recharge amount: {shortage_amount} to purchase the ticket"
# }

# Replace {shortage_amount} with the amount the user is short of the ticket's cost.

# Note: This amount may vary depending on whether you can find an optimal-cost route for the user. Sub-
# optimal solutions may be awarded with partial scores.

# Unreachable station
# If it is impossible to reach the destination station from the starting station, output a message with HTTP 403 -
# Forbidden and a message for the user.
# Response status: 403 - Forbidden
# Response model

# {
# "message": "no ticket available for station: {station_from} to station:
# {station_to}"
# }

# Replace {station_from} and {station_to} as specified in the input model.
# Examples

# Let's look at some example requests and responses.
# Example request:
# Request URL: [POST] http://localhost:8000/api/tickets
# Content Type: application/json
# Request Body:

# {
# "wallet_id": 3,
# "time_after": "10:55",
# "station_from": 1,
# "station_to": 5
# }

# Example successful response:
# Content Type: application/json
# HTTP Status Code: 201
# Response Body:

# {
# "ticket_id": 101,
# "balance": 43,
# "wallet_id": 3,
# "stations": [
# {
# "station_id": 1,
# "train_id": 3,
# "departure_time": "11:00",
# "arrival_time": null,
# },
# {
# "station_id": 3,
# "train_id": 2,
# "departure_time": "12:00",
# "arrival_time": "11:55"
# },
# {
# "station_id": 5,
# "train_id": 2,
# "departure_time": null,
# "arrival_time": "12:25"
# }

# ]
# }

# Example request for no tickets:
# Request URL: [POST] http://localhost:8000/api/tickets
# Content Type: application/json
# Request Body:

# {
# "wallet_id": 3,
# "time_after": "10:55",
# "station_from": 1,
# "station_to": 5
# }

# Example failed response:
# Content Type: application/json
# HTTP Status Code: 403
# Response Body:

# {
# "message": "no ticket available for station: 1 to station: 5"
# }

# Example request for insufficient funds:
# Request URL: [POST] http://localhost:8000/api/tickets
# Content Type: application/json
# Request Body:

# {
# "wallet_id": 3,
# "time_after": "10:55",
# "station_from": 1,
# "station_to": 5
# }

# Example failed response:

# Content Type: application/json
# HTTP Status Code: 402
# Response Body:

# {
# "message": "recharge amount: 113 to purchase the ticket"
# }

def get_minutes(time):
  hours, minutes = time.split(':')
  return int(hours)*60 + int(minutes)

def calculate_time(now_time, next_time):
    time_taken = 0
    if now_time < next_time:
        time_taken = next_time - now_time
    else:
        time_taken = 24*60 - now_time + next_time

    return time_taken


def find_best_route_within_time(station_from, station_to, time_after):
    best_route_cost = float('inf')
    best_route = []
    best_routes_time = float('inf')

    def recursive_search(current_station, station_to, current_time, time_left, current_cost, route):
        nonlocal best_route_cost, best_route, best_routes_time
        if time_left < 0:
            return

        if current_station == station_to:
            route = route + [
                {
                    "station_id": station_to,
                    "train_id": None,
                    "arrival_time": current_time,
                    "departure_time": None
                }
            ]
            if current_cost < best_route_cost:
                best_route_cost = current_cost
                best_route = route.copy()
                best_routes_time = 24*60 - time_left

            route.pop()
            return


        for next_station in db.get_next_stations(current_station):
            next_station_id, next_station_time, next_station_fare, train_taken = next_station
            next_station_time = get_minutes(next_station_time)
            time_taken = calculate_time(current_time, next_station_time)
            if time_taken > time_left:
                continue
            
            route = route + [
                {
                    "station_id": next_station_id,
                    "train_id": train_taken,
                    "arrival_time": current_time,
                    "departure_time": next_station_time
                }
            ]

            recursive_search(next_station_id, station_to, next_station_time, time_left - time_taken, current_cost + next_station_fare, route)
            route.pop()

    route = []
    recursive_search(station_from, station_to, get_minutes(time_after), 24*60, 0, route)

    def minute_to_time(minutes):
        if minutes == None:
            return None
        hours = minutes//60
        minutes = minutes%60
        return f"{hours:02d}:{minutes:02d}"
    
    best_route[0]['arrival_time'] = None

    for i in range(0, len(best_route)):
        best_route[i]['departure_time'] = minute_to_time(best_route[i]['departure_time'])
        best_route[i]['arrival_time'] = minute_to_time(best_route[i]['arrival_time'])

    return best_route_cost, best_route, best_routes_time

@app.post('/api/tickets', status_code=201)
def purchase_ticket(ticket: Dict):
    wallet_id = ticket['wallet_id']
    time_after = ticket['time_after']
    station_from = ticket['station_from']
    station_to = ticket['station_to']

    wallet = db.get_wallet(wallet_id)
    if not wallet:
        raise HTTPException(status_code=404, detail=f"wallet with id: {wallet_id} was not found")
    
    wallet_balance = wallet[2]

    best_route_cost, best_route, best_routes_time = find_best_route_within_time(station_from, station_to, time_after)

    if best_route_cost == float('inf'):
        raise HTTPException(status_code=403, detail=f"no ticket available for station: {station_from} to station: {station_to}")

    if wallet_balance < best_route_cost:
        shortage_amount = best_route_cost - wallet_balance
        raise HTTPException(status_code=402, detail=f"recharge amount: {shortage_amount} to purchase the ticket")

    new_balance = wallet_balance - best_route_cost
    db.update_wallet(wallet_id, new_balance)

    ticket_id = db.create_ticket(wallet_id, best_route_cost)

    response = {
        "ticket_id": ticket_id,
        "wallet_id": wallet_id,
        "balance": new_balance,
        "stations": best_route
    }

    return response


# use dict as schema
@app.post('/api/stations', status_code=201)
def create_station(station: Dict):
    return db.create_station(**station)

@app.post('/api/trains', status_code=201)
def create_train(train: Dict):
    return db.create_train(**train)



@app.get('/api/stations/{station_id}/trains')
def get_trains(station_id: int):
    station = db.get_station(station_id)
    if not station:
        return Response(content=json.dumps({"message": f"station with id: {station_id} was not found"}), status_code=404)
    trains = db.get_trains_from_station(station_id)
    modified_trains = []
    for train in trains:
        modified_trains.append({
            "train_id": train[0],
            "arrival_time": train[1],
            "departure_time": train[2],
        })
    return {
        "station_id": station_id,
        "trains": modified_trains
    }

@app.post('/api/users', status_code=201)
def create_station(user: Dict):
    return db.create_user(**user)

@app.get('/api/stations')
def get_stations():
    stations = db.get_stations()
    jsond_stations = []
    for station in stations:
        print(station)
        jsond_stations.append({'station_id': station[0], 'station_name': station[1], 'longitude': station[2], 'latitude': station[3]})
    
    return {'stations': jsond_stations}


@app.get('/api/wallets/{wallet_id}')
def get_wallet(wallet_id: int):
    wallet = db.get_wallet(wallet_id)
    print(wallet)
    if not wallet:
        return Response(content=json.dumps({"message": f"wallet with id: {wallet_id} was not found"}), status_code=404)
    
    response = {
        "wallet_id": wallet[0],
        "balance": wallet[2],
        "wallet_user": {
            "user_id": wallet[0],
            "user_name": wallet[1]
        }
    }

    return response


@app.put('/api/wallets/{wallet_id}', status_code=200)
def add_wallet_balance( wallet_id: int, recharge: Dict):
    recharge_amount = recharge['recharge']
    wallet = db.get_wallet(wallet_id)
    if not wallet:
        raise HTTPException(status_code=404, detail=f"wallet with id: {wallet_id} was not found")
    
    if recharge < 100 or recharge > 10000:
        raise HTTPException(status_code=400, detail=f"invalid amount: {recharge_amount}")

    new_balance = wallet[2] + recharge_amount
    db.update_wallet(wallet_id, new_balance)
    wallet = db.get_wallet(wallet_id)

    response = {
        "wallet_id": wallet[0],
        "balance": wallet[2],
        "wallet_user": {
            "user_id": wallet[0],
            "user_name": wallet[1]
        }
    }

    return response

