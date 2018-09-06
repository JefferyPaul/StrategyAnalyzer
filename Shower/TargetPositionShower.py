import pandas as pd
from datetime import *
import os
import DataManager
from Trader import Parse
from Trader.Trader import Trader
from pyecharts import Line, Grid


class TargetPositionShower:
	def __init__(self, invar_item, df_file_path, start_date, end_date):
		self.invar_item = invar_item
		self.df_file_path = pd.DataFrame(df_file_path)
		self.start_date = start_date
		self.end_date = end_date

	def show_target_position(self, signal_or_compare):
		if len(self.df_file_path) < 1:
			print(" Nothing to show , WRONG")
			return ""
		self.df_file_path = self.df_file_path[ self.df_file_path[ "Type" ] == "RawSignals" ]
		if signal_or_compare == "Compare":
			if len(self.df_file_path) < 2:
				print(" %s Not pair to Compare " % self.invar_item)
				return ""

		# 获取数据
		# 遍历所有trader
		list_df_price = [ ]
		list_df_target_position = [ ]
		for i_index in self.df_file_path.index:
			series_file_path = self.df_file_path.loc[ i_index, : ]
			path = {"RawSignals": series_file_path[ "Path" ]}
			trader_nameA = series_file_path[ "TraderA" ]
			strategy_name = series_file_path[ "Strategy" ]

			obj_trader_i = Trader(path, trader_nameA, strategy_name, self.start_date, self.end_date)
			obj_trader_i.get_target_position()
			df_trader_target_position = obj_trader_i.signal.std_target_position
			df_trader_price = obj_trader_i.signal.price
			list_df_target_position.append(df_trader_target_position)
			list_df_price.append(df_trader_price)

		df_target_position = pd.DataFrame(pd.concat(list_df_target_position, ignore_index=False))
		df_price = pd.DataFrame(pd.concat(list_df_price, ignore_index=False))

		# 计算合适的 y轴 x轴区间
		# x轴
		index_longer = pd.DataFrame()
		for i_strategy_traderA in df_target_position[ "Strategy_TraderA" ].unique().tolist():
			i_index = df_target_position.loc[ df_target_position[ "Strategy_TraderA" ] == i_strategy_traderA, : ].index
			if len(i_index) > len(index_longer):
				index_longer = i_index
		index_longer_max = max(index_longer)
		index_longer_min = min(index_longer)

		# 分别画图
		# 初始化图表
		grid = Grid(
			width=1200,
			height=700
		)
		line_mkp = Line()
		line_legend_top_position = 0
		line_legend_top_position_str = ""
		num_trader = len(self.df_file_path)
		gird_top_str = "%s%%" % str(int(5 * (num_trader + 1)))

		df_trader_price_longer = pd.DataFrame()
		list_ticker_name_longer = [ ]

		# 画band
		for i_strategy_traderA in df_target_position[ "Strategy_TraderA" ].unique().tolist():
			df_target_position_i = df_target_position.loc[
			                       df_target_position[ "Strategy_TraderA" ] == i_strategy_traderA, : ]
			df_price_i = df_price.loc[ df_price[ "Strategy_TraderA" ] == i_strategy_traderA, : ]
			strategy_name = i_strategy_traderA.split("_")[ 0 ]
			list_ticker_name = list(df_target_position_i[ 'Ticker' ].unique())

			line_target_position = Line()
			line_legend_top_position_str = "%s%%" % str(int(line_legend_top_position))
			line_legend_top_position += 5

			for i_ticker in list_ticker_name:
				series_target_position = df_target_position_i.loc[
					df_target_position_i[ "Ticker" ] == i_ticker, "TargetPosition" ]
				line_target_position.add(
					"%s-%s" % (strategy_name, i_ticker),
					x_axis=series_target_position.index.tolist(),
					y_axis=series_target_position.tolist(),
					yaxis_max=1,
					yaxis_min=-1,
					xaxis_max=index_longer_max,
					xaxis_min=index_longer_min,
					is_xaxis_show=False,
					is_datazoom_show=True,
					datazoom_xaxis_index=[ 0, 1, 2 ],
					legend_top=line_legend_top_position_str
				)

			grid.add(
				line_target_position,
				grid_top=gird_top_str
			)

			# 选择时间周期更长的MKP
			if len(list_ticker_name) > len(list_ticker_name_longer):
				list_ticker_name_longer = list_ticker_name
				df_trader_price_longer = df_price_i
			if len(df_price_i) > len(df_trader_price_longer) and \
					len(list_ticker_name) == len(list_ticker_name_longer):
				df_trader_price_longer = df_price_i

		# 画MKP
		line_legend_top_position_str = "%s%%" % str(int(line_legend_top_position))
		if len(df_trader_price_longer) > 0:
			line_mkp.add(
				"%s" % list(df_trader_price_longer[ "Ticker" ].unique())[ 0 ],
				x_axis=df_trader_price_longer.index.tolist(),
				y_axis=df_trader_price_longer[ 'Price' ].tolist(),
				yaxis_max=max(df_trader_price_longer),
				yaxis_min=min(df_trader_price_longer),
				xaxis_max=index_longer_max,
				xaxis_min=index_longer_min,
				yaxis_pos="right",
				datazoom_xaxis_index=[ 0, 1, 2 ],
				legend_top=line_legend_top_position_str
			)

		grid.add(
			line_mkp,
			grid_top=gird_top_str
		)
		return grid

#
#
# # 画targetPosition， 分ticker
# for i_ticker_name in list_ticker_name:
# 	df_ticker_std_target_position = df_trader_target_position.loc[
# 		df_trader_target_position[ "Ticker" ] == i_ticker_name,
# 		"TargetPosition"
# 	]
# 	line_targetP.add(
# 		"%s-%s" % (strategy_name, i_ticker_name),
# 		x_axis=df_ticker_std_target_position.index.tolist(),
# 		y_axis=[ round(i, 2) for i in df_ticker_std_target_position.tolist() ],
# 		is_datazoom_show=True,
# 		yaxis_max=1,
# 		yaxis_min=-1,
# 		datazoom_xaxis_index=[ 0, 1, 2 ],
# 		legend_top=line_legend_top_position_str
# 	)
#
#
#
# # 初始化图表
# grid = Grid()
# line_mkp = Line()
# line_targetP = Line()
# line_legend_top_position = 0
# line_legend_top_position_str = ""
# num_trader = len(self.df_file_path)
# gird_top_str = "%s%%" % str(int(10 * (num_trader+1)))
#
# df_trader_price_longer = pd.DataFrame()
# list_ticker_name_longer = []
#
#
#
#
# # 遍历所有trader
# for i_index in self.df_file_path.index:
# 	# 初始化图表
# 	line_targetP = Line()
#
# 	series_file_path = self.df_file_path.loc[i_index, :]
# 	path = {"RawSignals": series_file_path["Path"]}
# 	trader_nameA = series_file_path["TraderA"]
# 	strategy_name = series_file_path["Strategy"]
#
# 	# Trader对象实例化，获取数据
# 	obj_trader_i = Trader(path, trader_nameA, strategy_name, self.start_date, self.end_date)
# 	obj_trader_i.get_target_position()
#
# 	'''
# 	数据格式
# 	target_position, df ["Ticker", "TargetPosition"] index="DateTime"
# 	df_trader_price, df ["Ticker", "price"] index="DateTime"   price or pair_price
# 	'''
# 	df_trader_target_position = obj_trader_i.signal.std_target_position
# 	df_trader_price = obj_trader_i.signal.price
# 	list_ticker_name = list(df_trader_target_position['Ticker'].unique())
#
# 	line_legend_top_position_str = "%s%%" % str(int(line_legend_top_position))
# 	line_legend_top_position += 10
#
# 	# 画targetPosition， 分ticker
# 	for i_ticker_name in list_ticker_name:
# 		df_ticker_std_target_position = df_trader_target_position.loc[
# 			df_trader_target_position["Ticker"] == i_ticker_name,
# 			"TargetPosition"
# 		]
# 		line_targetP.add(
# 			"%s-%s" % (strategy_name, i_ticker_name),
# 			x_axis=df_ticker_std_target_position.index.tolist(),
# 			y_axis=[ round(i, 2) for i in df_ticker_std_target_position.tolist() ],
# 			is_datazoom_show=True,
# 			yaxis_max=1,
# 			yaxis_min=-1,
# 			datazoom_xaxis_index=[0, 1, 2],
# 			legend_top=line_legend_top_position_str
# 		)
#
# 	grid.add(
# 		line_targetP,
# 		grid_top=gird_top_str
# 	)
#
# 	# 选择时间周期更长的MKP
# 	if len(list_ticker_name) > len(list_ticker_name_longer):
# 		list_ticker_name_longer = list_ticker_name
# 		df_trader_price_longer = df_trader_price
# 	if len(df_trader_price) > len(df_trader_price_longer) and \
# 			len(list_ticker_name) == len(list_ticker_name_longer):
# 		df_trader_price_longer = df_trader_price
#
# # 画MKP
# line_legend_top_position_str = "%s%%" % str(int(line_legend_top_position))
# if len(df_trader_price_longer) > 0:
# 	line_mkp.add(
# 		"%s" % list(df_trader_price_longer["Ticker"].unique())[0],
# 		x_axis=df_trader_price_longer.index.tolist(),
# 		y_axis=df_trader_price_longer['Price'].tolist(),
# 		# yaxis_max=round(max(df_trader_price_longer['MarketPrice'].tolist()), radix_point + 2) + (0.1 ** (radix_point+2)),
# 		# yaxis_min=round(min(df_trader_price_longer['MarketPrice'].tolist()), radix_point + 2) - (0.1 ** (radix_point+2)),
# 		yaxis_max=max(df_trader_price_longer['Price'].tolist()),
# 		yaxis_min=min(df_trader_price_longer['Price'].tolist()),
# 		yaxis_pos="right",
# 		is_datazoom_show=True,
# 		datazoom_xaxis_index=[0, 1, 2],
# 		legend_top=line_legend_top_position_str
# 	)
# else:
# 	return ""
#
# grid.add(
# 	line_mkp,
# 	grid_top=gird_top_str
# )
#
# return grid
