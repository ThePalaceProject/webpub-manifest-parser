# import json
# import os
#
# import requests
# from jsonschema import validate
#
# # response = requests.get('https://raw.githubusercontent.com/opds-community/drafts/master/schema/feed.schema.json')
# # json_schema = response.json()
#
#
# input_file_path = os.path.join(
#     os.path.dirname(__file__), "../../files/schema/opds2/feed.schema.json"
# )
# with open(input_file_path, 'r') as input_file:
#     json_schema = json.load(input_file)
#
# def validate_json(json_data, json_schema):
#     validate(instance=json_data, schema=json_schema)
#
#
#
# input_file_path = os.path.join(
#     os.path.dirname(__file__), "../../files/opds2/test.json"
# )
#
# with open(input_file_path, 'r') as input_file:
#     json_data = json.load(input_file)
#
#     validate_json(json_data, json_schema)
#
