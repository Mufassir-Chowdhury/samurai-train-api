import sqlite3

class TrainService():
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users(
                            user_id INTEGER PRIMARY KEY, 
                            user_name TEXT,
                            balance INTEGER
                    )''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS stations(
                            station_id INTEGER PRIMARY KEY, 
                            station_name TEXT, 
                            longitude REAL, 
                            latitude REAL
                    )''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS trains(
                            train_id INTEGER PRIMARY KEY, 
                            train_name TEXT, 
                            capacity INTEGER
                    )''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS train_stops(
                            train_id INTEGER, 
                            station_id INTEGER, 
                            arrival_time TEXT, 
                            departure_time TEXT, 
                            fare INTEGER
                    )''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS tickets(
                            ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            wallet_id INTEGER,
                            time_after TEXT,
                            station_from INTEGER,
                            station_to INTEGER
                    )''')

        self.conn.commit()

    def create_user(self, user_id, user_name, balance):
        self.cursor.execute('INSERT INTO users VALUES(?, ?, ?)', (user_id, user_name, balance))
        self.conn.commit()
        return {'user_id': user_id, 'user_name': user_name, 'balance': balance}

    def create_station(self, station_id, station_name, longitude, latitude):
        self.cursor.execute('INSERT INTO stations VALUES(?, ?, ?, ?)', (station_id, station_name, longitude, latitude))
        self.conn.commit()
        return {'station_id': station_id, 'station_name': station_name, 'longitude': longitude, 'latitude': latitude}

    def create_train(self, train_id, train_name, capacity, stops):
        self.cursor.execute('INSERT INTO trains VALUES(?, ?, ?)', (train_id, train_name, capacity))
        for stop in stops:
            self.cursor.execute('INSERT INTO train_stops VALUES(?, ?, ?, ?, ?)', (train_id, stop['station_id'], stop['arrival_time'], stop['departure_time'], stop['fare']))
        self.conn.commit()
        return {'train_id': train_id, 'train_name': train_name, 'capacity': capacity, 'service_start': stops[0]['departure_time'], 'service_ends': stops[-1]['arrival_time'], 'num_stations': len(stops)}

    def get_station(self, station_id):
        self.cursor.execute('SELECT * FROM stations WHERE station_id = ?', (station_id,))
        return self.cursor.fetchone()
    
    def create_ticket(self, wallet_id, time_after, station_from, station_to):
        self.cursor.execute('INSERT INTO tickets(wallet_id, time_after, station_from, station_to) VALUES(?, ?, ?, ?)', (wallet_id, time_after, station_from, station_to))
        ticket_id = self.cursor.lastrowid
        self.conn.commit()
        stations = self.get_stations()


    def get_stations(self):
        self.cursor.execute('SELECT * FROM stations')
        return self.cursor.fetchall()

    def get_users(self):
        self.cursor.execute('SELECT * FROM users')
        return self.cursor.fetchall()

    def get_trains(self):
        self.cursor.execute('SELECT * FROM trains')
        return self.cursor.fetchall()

    def get_train_stops(self, train_id):
        self.cursor.execute('SELECT * FROM train_stops WHERE train_id = ?', (train_id,))
        return self.cursor.fetchall()
    
    def get_trains_from_station(self, station_id):
        trains = []
        self.cursor.execute('SELECT train_id, arrival_time, departure_time FROM train_stops WHERE station_id = ?', (station_id,))
        trains = self.cursor.fetchall()
        return trains
    
    def get_wallet(self, wallet_id):
        self.cursor.execute('SELECT * FROM users WHERE user_id = ?', (wallet_id,))
        return self.cursor.fetchone()
    
    def update_wallet(self, wallet_id, amount):
        self.cursor.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (amount, wallet_id))
        self.conn.commit()
        return self.get_wallet(wallet_id)
    
    def all_next_stations(self, station_id):
        # returns list of next_station_id, next_station_time, next_station_fare, train_taken
        trains = self.get_trains_from_station(station_id)
        next_stations = []
        for train in trains:
            stops = self.get_train_stops(train[0])
            for stop in stops:
                if stop[1] == station_id:
                    next_stations.append((stop[1], stop[3], stop[4], train[0]))
        return next_stations

