import os

if not os.getenv("CONTAINER_RUNNING"):
    from dotenv import load_dotenv

    print("Running on local environment.")
    load_dotenv()

database_credentials = {"host": os.getenv("ENV_DB_HOST"),
                        "name": os.getenv("ENV_DB_NAME"),
                        "user": os.getenv("ENV_DB_USER"),
                        "pwd": os.getenv("ENV_DB_PWD")
                        }

expected_api_call_fields = {"key": "apiKey",
                            "datetime": "datetime",
                            "temperature": "temperature",
                            "humidity": "humidity",
                            "time": "time"
                            }
