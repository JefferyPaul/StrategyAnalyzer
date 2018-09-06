import json
import os
import pandas as pd
from datetime import *


def str_to_datetime(str_start, str_end):
	if len(str_start) == 0:
		start_date = datetime(2000, 1, 1)
	else:
		start_date = datetime.strptime(str_start, "%Y-%m-%d")
	if len(str_end) == 0:
		end_date = datetime(2020, 1, 1)
	else:
		end_date = datetime.strptime(str_end, "%Y-%m-%d")
	return start_date, end_date


def get_config():
	path = r"..\config.json"
	with open(path, "r", encoding='UTF-8') as f:
		dict_config = json.loads(f.read())

	dict_config[ "start_date" ], dict_config[ "end_date" ] \
		= str_to_datetime(dict_config[ "start_date" ], dict_config[ "end_date" ])

	return dict_config
