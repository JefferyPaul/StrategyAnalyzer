import pandas as pd
from datetime import *
from Trader.Trader import Trader
from pyecharts import Line, Grid
import numpy as np


class TargetPositionShower:
	def __init__(self, invar_item, df_file_path, start_date, end_date, dt_round_level):
		self.invar_item = invar_item
		self.df_file_path = pd.DataFrame(df_file_path)
		self.start_date = start_date
		self.end_date = end_date
		self.dt_round_level = dt_round_level

	# 获取数据
	# 遍历所有trader

	def get_data(self):
		list_df_price = []
		list_df_target_position = []
		for i_index in self.df_file_path.index:
			series_file_path = self.df_file_path.loc[i_index, :]
			path = {"RawSignals":series_file_path["Path"]}
			trader_nameA = series_file_path["TraderA"]
			strategy_name = series_file_path["Strategy"]

			obj_trader_i = Trader(path, trader_nameA, strategy_name, self.start_date, self.end_date,
			                      self.dt_round_level)
			obj_trader_i.get_target_position()
			df_trader_target_position = obj_trader_i.signal.std_target_position
			df_trader_price = obj_trader_i.signal.price
			list_df_target_position.append(df_trader_target_position)
			# 选择价格。     多trader，pair优先
			list_df_price.append(df_trader_price)

		df_target_position = pd.DataFrame(pd.concat(list_df_target_position, ignore_index=False))
		df_price = pd.DataFrame(pd.concat(list_df_price, ignore_index=False))

		df_target_position_pv = pd.pivot_table(
			df_target_position,
			index="DateTime",
			columns=["Strategy_TraderA", "Ticker"],
			values="TargetPosition",
			aggfunc=np.mean
		)
		df_target_position_pv = df_target_position_pv.sort_index(axis=1, level=[0, 1])
		df_price_pv = pd.pivot_table(
			df_price,
			index="DateTime",
			columns="Strategy_TraderA",
			values="Price",
			aggfunc=np.mean
		)
		df_price_pv = df_price_pv.sort_index(axis=1, level=0)

		df_target_position_pv = df_target_position_pv.fillna(method='ffill')
		df_price_pv = df_price_pv.fillna(method='ffill')
		return df_target_position_pv, df_price_pv

	def show_target_position(self, single_or_compare):
		if len(self.df_file_path) < 1:
			print(" Nothing to show , WRONG")
			return ""
		self.df_file_path = self.df_file_path[self.df_file_path["Type"] == "RawSignals"]
		if single_or_compare == "Compare":
			if len(self.df_file_path) < 2:
				print(" %s Not pair to Compare " % self.invar_item)
				return ""

		df_target_position_pv, df_price_pv = self.get_data()
		list_df_tp_trader = list(set(df_target_position_pv.columns.get_level_values("Strategy_TraderA").tolist()))
		num_df_tp_trader = len(list_df_tp_trader)
		gird_top_str = "%s%%" % str(int(5 * (num_df_tp_trader + 1)))

		# 计算合适的 y轴 x轴区间
		# x轴
		index_tp = df_target_position_pv.index.tolist()
		df_price_pv.index = index_tp
		index_longer_max = max(index_tp)
		index_longer_min = min(index_tp)

		# 分别画图
		# 初始化图表
		grid = Grid(
			width=1200,
			height=700
		)

		# 画tp
		line_mkp = Line()
		line_target_position = Line()
		for columns_index in df_target_position_pv.columns:
			name_Strategy_TraderA = columns_index[0]
			ticker_name = columns_index[1]
			series_tp_trader = df_target_position_pv[columns_index]

			num_trader = list_df_tp_trader.index(name_Strategy_TraderA)
			line_legend_top_position_str = "%s%%" % str(int(num_trader) * 5)
			print(list_df_tp_trader, name_Strategy_TraderA, num_trader, line_legend_top_position_str)

			line_target_position.add(
				"%s-%s" % (name_Strategy_TraderA, ticker_name),
				x_axis=index_tp,
				y_axis=series_tp_trader.tolist(),
				yaxis_max=1,
				yaxis_min=-1,
				xaxis_max=index_longer_max,
				xaxis_min=index_longer_min,
				is_xaxis_show=False,
				is_datazoom_show=True,
				datazoom_xaxis_index=[0, 1],
				legend_top=line_legend_top_position_str
			)

		grid.add(
			line_target_position,
			grid_top=gird_top_str
		)

		# 画MKP
		line_legend_top_position_str = "%s%%" % str(int(num_df_tp_trader) * 5)
		series_market_price = df_price_pv[df_price_pv.columns.tolist()[0]]
		line_mkp.add(
			"%s" % df_price_pv.columns.tolist()[0],
			x_axis=index_tp,
			y_axis=series_market_price.tolist(),
			yaxis_max=max(series_market_price.tolist()),
			yaxis_min=min(series_market_price.tolist()),
			xaxis_max=index_longer_max,
			xaxis_min=index_longer_min,
			is_xaxis_show=True,
			yaxis_pos="right",
			is_datazoom_show=True,
			datazoom_xaxis_index=[0, 1],
			legend_top=line_legend_top_position_str
		)

		grid.add(
			line_mkp,
			grid_top=gird_top_str
		)
		return grid
