from fastapi import FastAPI
from pydantic import BaseModel
import datetime
import json

import database.database as db
import src.config as config


class Sensor(BaseModel):
    apiKey: str
    temperature: float
    humidity: float
    datetime: str
    battery: float


app = FastAPI()
database = db.Database(host=config.database_credentials["host"],
                       name=config.database_credentials["name"],
                       user=config.database_credentials["user"],
                       pwd=config.database_credentials["pwd"])


@app.get("/time")
def read_time():
    return {"Time": f"{datetime.datetime.now()}"}


@app.post("/post-data")
def add_sensor_data(sensor: Sensor):
    response = {}
    api_keys = database.fetch_api_keys()

    if sensor.apiKey in api_keys:
        database_insert_success = database.insert_sensor_data(
            api_key=sensor.apiKey,
            datetime=sensor.datetime,
            temperature=sensor.temperature,
            humidity=sensor.humidity,
            battery=sensor.battery)
        if database_insert_success:
            response["Status"] = "OK"
            return response

        response.clear()
        response["Error"] = f"Error while inserting data in the database."
        return response

    response.clear()
    response["Error"] = f"API given invalid API key: {sensor.apiKey} "
    return response


@app.get("/sensors-data")
def get_sensors_data():
    response = {}
    log = database.fetch_sensor_log(max_rows=2)
    for field in log:
        field_data = {"time": field[1].strftime("%Y/%m/%d, %H:%M:%S"),
                      "temperature": field[2],
                      "humidity": field[3],
                      "battery": field[4]}
        (response.setdefault(field[0], [field_data])
         if field[0] not in response.keys()
         else response[field[0]].append(field_data))
    return response


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
