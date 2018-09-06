import os
from datetime import *
import pandas as pd

'''
输入目标strategies，目标traders，和数据所在folder
data folder结构： " data folder / strategy name / trader name / data.csv 
(RawSignals.csv / RawArbSignals.csv / SIG.csv / Band.csv)
当chose_strategies == [] , chose_strategies = all
当chose_traders == [] , chose_traders = all

返回 dict_data_folder_path
 = { strategy_name: { trader_name_A : trader_folder_path }, }
'''
'''
    data目录结构
    type 1,Sim:
        root_data_path
            strategy_folder
                trader_folder
                    RawSignal.csv
                    RawArbSignal.csv
    type 2,Live:
        root_data_path
            strategy_folder
                SIG_xxx.csv
                SIG_yyy.csv
                BAND_xxx.csv
                BAND_yyy.csv
'''
'''
    df_data_file_path, 
    columns=[ Strategy, TraderA, Type, Path]
'''


def get_data_path(chose_strategies, chose_traders, path_root):
	def get_live_data_path(path_strategy_folder, list_strategy_folder):
		for i_file_name in list_strategy_folder:
			if i_file_name.find("_") == -1:
				continue
			data_type = i_file_name.split("_")[ 0 ]
			if data_type not in [ "BAND", "SIG" ]:
				continue
			if data_type == "BAND":
				file_type = "RawArbSignals"
			if data_type == "SIG":
				file_type = "RawSignals"

			trader_name = i_file_name[
			              i_file_name.find("_") + 1:-4
			              ]
			trader_nameA = trader_name.split("@")[ 0 ]
			strategy_traderA = "%s-%s" % (strategy_name, trader_nameA)
			i_file_path = os.path.join(path_strategy_folder, i_file_name)

			list_data_file_path.append(
				[ strategy_name,
				  trader_nameA,
				  strategy_traderA,
				  file_type,
				  i_file_path ]
			)

	def get_sim_data_path(path_strategy_folder, list_strategy_folder):
		for i_trader_name in list_strategy_folder:
			path_trader_folder = os.path.join(
				path_strategy_folder, i_trader_name
			)
			list_trader_folder = os.listdir(path_trader_folder)
			for i_file_name in list_trader_folder:
				if i_file_name not in [ "RawSignals.csv", "RawArbSignals.csv" ]:
					continue
				i_file_path = os.path.join(path_trader_folder, i_file_name)
				trader_nameA = i_trader_name.split("@")[ 0 ]
				strategy_traderA = "%s-%s" % (strategy_name, trader_nameA)

				file_type = i_file_name.split(".")[ 0 ]

				list_data_file_path.append(
					[ strategy_name,
					  trader_nameA,
					  strategy_traderA,
					  file_type,
					  i_file_path ]
				)

	# 1 获取地址
	list_data_file_path = [ ]
	for strategy_name in os.listdir(path_root):
		if type(chose_strategies) == list:
			if strategy_name not in chose_strategies:
				continue

		path_strategy_folder = os.path.join(path_root, strategy_name)
		list_strategy_folder = os.listdir(path_strategy_folder)
		if len(list_strategy_folder) < 1:
			print("%s    has nothing" % path_strategy_folder)
			continue

		# 分 Live 与 Sim 两种不同数据目录结构录入
		# 不筛选trader， 全部录入
		if os.path.isfile(
				os.path.join(path_strategy_folder, list_strategy_folder[ 0 ])):
			get_live_data_path(path_strategy_folder, list_strategy_folder)
		else:
			get_sim_data_path(path_strategy_folder, list_strategy_folder)

	df_data_file_path = pd.DataFrame(
		list_data_file_path,
		columns=[ "Strategy", "TraderA", "strategy_traderA", "Type", "Path" ]
	)

	# 筛选trader
	# 若有目标trader, 录入目标trader path，
	# 若chose_traders == [], 录入该strategy下的所有traders
	if chose_traders == [ ]:
		df_data_file_path = df_data_file_path
	else:
		df_data_file_path = df_data_file_path.loc[
		                    [ i in chose_traders for i in df_data_file_path[ "TraderA" ] ], :
		                    ]

	return df_data_file_path
