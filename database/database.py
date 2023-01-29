import mysql.connector
from mysql.connector import Error


class Database:
    def __init__(self, host, name, user, pwd):
        self._host = host
        self._name = name
        self._user = user
        self._pwd = pwd

    @property
    def host(self):
        return self._host

    @property
    def name(self):
        return self._name

    @property
    def user(self):
        return self._user

    @property
    def pwd(self):
        return self._pwd

    def fetch_api_keys(self):
        data = self._request_data("SELECT apiAPIKey FROM tblAPIKey")
        curated_data = [item[0] for item in data]
        return curated_data

    def fetch_sensor_log(self, max_rows=24):
        data = self._request_data(
            f"SELECT Location, Time, Temperature, Humidity, Battery "
            f"FROM (SELECT tblSensor.senPlacement AS Location, "
            f"logtblClimateData.cliTime AS Time, "
            f"logtblClimateData.cliTemperature AS Temperature, "
            f"logtblClimateData.cliHumidity as Humidity, "
            f"logtblClimateData.cliBattery as Battery, "
            f"row_number() OVER (PARTITION BY tblSensor.senPlacement "
            f"ORDER BY logtblClimateData.cliTime DESC) AS row "
            f"FROM logtblClimateData "
            f"INNER JOIN tblSensor "
            f"ON logtblClimateData.cliSensorID=tblSensor.senSensorID "
            f"ORDER BY tblSensor.senPlacement ASC, "
            f"logtblClimateData.cliTime DESC) AS foo "
            f"WHERE row<={max_rows}"
        )
        print(data)
        return data

    def _request_data(self, mysql_request: str):
        if type(mysql_request) is not str:
            raise TypeError
        conn = None
        try:
            conn = mysql.connector.connect(host=self._host,
                                           database=self._name,
                                           user=self._user,
                                           password=self._pwd)
            cursor = conn.cursor()
            cursor.execute(mysql_request)
            return cursor.fetchall()

        except Error as e:
            print(e)

        finally:
            if conn is not None and conn.is_connected():
                conn.close()

    def insert_sensor_data(
            self, api_key, datetime, temperature, humidity, battery):
        return self._insert_data(
            f"INSERT INTO logtblClimateData "
            f"(cliSensorID, cliTime, cliTemperature, cliHumidity, cliBattery) "
            f"VALUES ("
            f"(SELECT apiSensorID FROM tblAPIKey "
            f"WHERE apiAPIKey = '{api_key}'), "
            f"'{datetime}', {temperature}, {humidity}, {battery}) ")

    def _insert_data(self, mysql_request):
        if type(mysql_request) is not str:
            raise TypeError
        conn = None
        try:
            conn = mysql.connector.connect(host=self._host,
                                           database=self._name,
                                           user=self._user,
                                           password=self._pwd)
            cursor = conn.cursor()
            cursor.execute(mysql_request)
            conn.commit()
            return True

        except Error as e:
            print(f"Error when inserting data to the database - {e}")

        finally:
            if conn is not None and conn.is_connected():
                conn.close()
