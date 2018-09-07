import pandas as pd
import numpy as np
from datetime import *
import DataManager
from Trader.Trader import Trader
from pyecharts import Line, Grid


class BandShower:
	def __init__(self, invar_item, df_file_path, start_date, end_date, dt_round_level):
		self.invar_item = invar_item
		self.df_file_path = pd.DataFrame(df_file_path)
		self.start_date = start_date
		self.end_date = end_date
		self.dt_round_level = dt_round_level

	def get_data(self, ):
		l_band_data = []
		for i_index in self.df_file_path.index:
			series_file_path = self.df_file_path.loc[i_index, :]
			path = {"RawArbSignals":series_file_path["Path"]}
			trader_nameA = series_file_path["TraderA"]
			strategy_name = series_file_path["Strategy"]
			obj_trader_i = Trader(path, trader_nameA, strategy_name, self.start_date, self.end_date,
			                      self.dt_round_level)
			obj_trader_i.get_band()
			df_band = obj_trader_i.signal.band
			l_band_data.append(df_band)

		# 计算最大最小值
		df_band_all = pd.DataFrame(pd.concat(l_band_data, ignore_index=False))
		max_px = max(
			max(df_band_all["BuyEntry"]),
			max(df_band_all["BuyExit"]),
			max(df_band_all["SellEntry"]),
			max(df_band_all["SellExit"]),
			max(df_band_all["Price"])
		)
		min_px = min(
			min(df_band_all["BuyEntry"]),
			min(df_band_all["BuyExit"]),
			min(df_band_all["SellEntry"]),
			min(df_band_all["SellExit"]),
			min(df_band_all["Price"])
		)

		df_band_pv = pd.pivot_table(
			df_band_all,
			index="DateTime",
			columns=["Strategy_TraderA", "Ticker"],
			values=[
				"BuyEntry",
				"BuyExit",
				"SellEntry",
				"SellExit",
			],
			aggfunc=np.mean
		)

		df_price_pv = pd.pivot_table(
			df_band_all,
			index="DateTime",
			columns=["Strategy_TraderA", "Ticker"],
			values="Price",
			aggfunc=np.mean
		)

		df_band_pv = df_band_pv.fillna(method='ffill')
		return df_band_pv, df_price_pv, max_px, min_px

	def show_band(self, single_or_compare):
		if len(self.df_file_path) < 1:
			print(" Nothing to show , WRONG")
			return ""
		self.df_file_path = self.df_file_path[self.df_file_path["Type"] == "RawArbSignals"]
		if single_or_compare == "Compare":
			if len(self.df_file_path) < 2:
				print("%s Not pair to Compare " % self.invar_item)
				return ""

		# 获取数据
		df_band_pv, df_price_pv, max_px, min_px = self.get_data()

		list_df_band_trader = list(set(df_band_pv.columns.get_level_values("Strategy_TraderA").tolist()))
		num_df_band_trader = len(list_df_band_trader)
		gird_top_str = "%s%%" % str(int(5 * (num_df_band_trader + 1)))

		# x轴
		index_band = df_band_pv.index.tolist()
		index_max = max(index_band)
		index_min = min(index_band)

		# 分别画图
		# 初始化图表
		grid = Grid(
			width=1200,
			height=700
		)

		# 画band
		line_band = Line()
		for columns_index in df_band_pv.columns:
			band_type = columns_index[0].split("_")[0]
			name_Strategy_TraderA = columns_index[1]
			series_band_trader = df_band_pv[columns_index]

			num_trader = list_df_band_trader.index(name_Strategy_TraderA)
			line_legend_top_position_str = "%s%%" % str(int(num_trader) * 5)

			line_band.add(
				"%s-%s" % (name_Strategy_TraderA, band_type),
				x_axis=index_band,
				y_axis=series_band_trader.tolist(),
				yaxis_max=max_px,
				yaxis_min=min_px,
				xaxis_max=index_max,
				xaxis_min=index_min,
				is_xaxis_show=False,
				is_datazoom_show=True,
				datazoom_xaxis_index=[0, 1],
				legend_top=line_legend_top_position_str
			)

		grid.add(
			line_band,
			grid_top=gird_top_str
		)

		# 画MKP
		line_mkp = Line()
		line_legend_top_position_str = "%s%%" % str(int(num_df_band_trader) * 5)
		series_market_price = df_price_pv[df_price_pv.columns.tolist()[0]]
		line_mkp.add(
			"%s" % "t",
			x_axis=index_band,
			y_axis=series_market_price.tolist(),
			# yaxis_max=max(series_market_price.tolist()),
			# yaxis_min=min(series_market_price.tolist()),
			yaxis_max=max_px,
			yaxis_min=min_px,
			xaxis_max=index_max,
			xaxis_min=index_min,
			yaxis_pos="right",
			is_xaxis_show=True,
			is_datazoom_show=True,
			datazoom_xaxis_index=[0, 1],
			legend_top=line_legend_top_position_str
		)

		grid.add(
			line_mkp,
			grid_top=gird_top_str
		)
		return grid
