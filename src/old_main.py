from flask import Flask, jsonify, request

import src.config as config
import database.database as database

app = Flask("API")


@app.route('/post-data', methods=['GET'])
def main():
	expected_fields = [config.expected_api_call_fields[key] for key in config.expected_api_call_fields.keys()]
	response = {}
	posted_data = {}

	# Check that all fields are present and entered correctly
	# If not, answer with an error and mention which fields are incorrect/missing
	for field in expected_fields:
		if request.args.get(field) is None:
			if "Error" in response.keys():
				response["Error"] += f", '{field}'"
			else:
				response.clear()
				response["Error"] = f"Invalid or missing field, expected: '{field}'"
		else:
			if "Error" not in response.keys():
				posted_data[field] = request.args.get(field)
	if "Error" in response.keys():
		return jsonify(response)

	indoor_climate_database = database.Database(host=config.database_credentials["host"],
												name=config.database_credentials["name"],
												user=config.database_credentials["user"],
												pwd=config.database_credentials["pwd"])

	posted_key = posted_data[config.expected_api_call_fields["key"]]
	api_keys = indoor_climate_database.fetch_api_keys()

	for key in api_keys:
		if key == posted_key:
			print(f"API_Key {key} has been authenticated.")
			response["Error"] = "0"
			indoor_climate_database.insert_sensor_data(api_key=posted_data[config.expected_api_call_fields["key"]],
													   datetime=posted_data[config.expected_api_call_fields["datetime"]],
													   temperature=posted_data[config.expected_api_call_fields["temperature"]],
													   humidity=posted_data[config.expected_api_call_fields["humidity"]])
			return jsonify(response)

	response.clear()
	response["Error"] = f"API given {posted_data}"
	return jsonify(response)


if __name__ == '__main__':
	app.run(debug=True, host="0.0.0.0", port=8000)
