import os
import pandas as pd
from datetime import *
from Checker.getConfig import get_config
from DataManager import get_data_path
from Shower.BandShower import BandShower
from Shower.TargetPositionShower import TargetPositionShower


def set_start_date(str_start):
	if len(str_start) == 0:
		start_date = datetime(2000, 1, 1)
	else:
		start_date = datetime.strptime(str_start, "%Y-%m-%d")
	return start_date


def set_end_date(str_end):
	if len(str_end) == 0:
		end_date = datetime(2020, 1, 1)
	else:
		end_date = datetime.strptime(str_end, "%Y-%m-%d")
	return end_date


'''
    1 SimulationSignals VS SimulationSignals
    2 SimulationSignals VS liveSignals
    仅在 Trader-Signal.py中读取文件时的文件名有区分，数据结构和对比流程不存在区别
'''
if __name__ == '__main__':
	#
	# 1 参数获取
	dict_config = get_config()
	path_input_folder = dict_config["path_input_folder"]
	path_output_folder = dict_config["path_output_folder"]
	list_strategies = dict_config["strategies"]
	list_traders = dict_config["traders"]
	compare_match_mode = dict_config["compare_match_mode"]
	show_mode = dict_config["show_mode"]
	compare_mode = dict_config["compare_mode"]
	dt_round_level = dict_config["dt_round_level"]

	if type(dict_config["start_date"]) == str:
		start_date = set_start_date(dict_config["start_date"])
	else:
		start_date = dict_config["start_date"]
	if type(dict_config["end_date"]) == str:
		end_date = set_end_date((dict_config["end_date"]))
	else:
		end_date = dict_config["end_date"]

	# 2 获取所需对比的策略的数据所在的目录
	df_data_file_path = pd.DataFrame(
		get_data_path(list_strategies, list_traders, path_input_folder))
	print(df_data_file_path["Path"])

	# 3 获取并整理数据
	# 4 画图展示
	py_start_time_t = datetime.now().strftime("%H:%M:%S")
	py_start_time = datetime.now().strftime("%Y%m%d_%H%M%S")
	print(py_start_time)

	'''
	根据compare需求，compare_match_mode分为：
	1 不同strategy 同trader ticker比较
	2 同strategy 不同trader ticker比较
	3 不配对，逐一显示
	'''
	if compare_match_mode == "1":
		df_data_file_path_gb = df_data_file_path.groupby("TraderA")
	elif compare_match_mode == "2":
		df_data_file_path_gb = df_data_file_path.groupby("Strategy")
	elif compare_match_mode == "3":
		df_data_file_path_gb = df_data_file_path.groupby("strategy_traderA")
	else:
		print("compare_match_mode    is Wrong,  changed in mode '3'")
		df_data_file_path_gb = df_data_file_path.groupby("strategy_traderA")

	# 遍历所有对比项
	for invar_item, df_data_file_path_i in df_data_file_path_gb:
		'''
		show_mode分为：
		1 TargetPosition 对比
		2 Band 对比
		3 Both
		
		compare_mode分为：
		Single : 单独一个trader也展示--展示所有path中的内容；
		Compare: 仅当path中存在多于或等于2个 相同类型的trader时才展示，用于对比，不对比数据不足的内容。
		'''

		if show_mode == "1" or show_mode == "3":
			tp = TargetPositionShower(invar_item, df_data_file_path_i, start_date, end_date, dt_round_level)
			if compare_mode == "2":
				grid = tp.show_target_position("Single")
			else:
				grid = tp.show_target_position("Compare")
			if grid == "":
				continue

			output_path_folder = r"%s/%s" % (path_output_folder, py_start_time)
			if not os.path.exists(output_path_folder):
				os.mkdir(output_path_folder)
			grid.render(
				r"%s/%s-targetPosition.html" % (
					output_path_folder,
					invar_item)
			)
			print(" %s - TargetPosition  Done " % invar_item)

		if show_mode == "2" or show_mode == "3":
			tp = BandShower(invar_item, df_data_file_path_i, start_date, end_date, dt_round_level)
			if compare_mode == "2":
				grid = tp.show_band("Signal")
			else:
				grid = tp.show_band("Compare")
			if grid == "":
				continue

			output_path_folder = r"%s/%s" % (path_output_folder, py_start_time)
			if not os.path.exists(output_path_folder):
				os.mkdir(output_path_folder)
			grid.render(
				r"%s/%s-band.html" % (
					output_path_folder,
					invar_item)
			)
			print(" %s -  band           Done " % invar_item)

	print("    Start at : %s " % py_start_time_t)
	print(" Finished at : %s " % datetime.now().strftime("%H:%M:%S"))
	print(" ALL FINISHED")
