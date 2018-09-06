import pandas as pd
from datetime import *
import os
import DataManager
from Trader import Parse
from Trader.Trader import Trader
from pyecharts import Line, Grid


class BandShower:
	def __init__(self, invar_item, df_file_path, start_date, end_date):
		self.invar_item = invar_item
		self.df_file_path = pd.DataFrame(df_file_path)
		self.start_date = start_date
		self.end_date = end_date

	def show_band(self, signal_or_compare):
		if len(self.df_file_path) < 1:
			print(" Nothing to show , WRONG")
			return ""

		self.df_file_path = self.df_file_path[ self.df_file_path[ "Type" ] == "RawArbSignals" ]

		if signal_or_compare == "Compare":
			if len(self.df_file_path) < 2:
				print("%s Not pair to Compare " % self.invar_item)
				return ""

		# 获取数据
		# 遍历所有trader
		l_band_data = [ ]
		for i_index in self.df_file_path.index:
			series_file_path = self.df_file_path.loc[ i_index, : ]
			path = {"RawArbSignals": series_file_path[ "Path" ]}
			trader_nameA = series_file_path[ "TraderA" ]
			strategy_name = series_file_path[ "Strategy" ]
			obj_trader_i = Trader(path, trader_nameA, strategy_name, self.start_date, self.end_date)
			obj_trader_i.get_band()
			df_band = obj_trader_i.signal.band
			l_band_data.append(df_band)

		# 计算合适的 y轴 x轴区间
		df_band = pd.DataFrame(pd.concat(l_band_data, ignore_index=False))
		max_px = max(
			max(df_band[ "BuyEntry" ]),
			max(df_band[ "BuyExit" ]),
			max(df_band[ "SellEntry" ]),
			max(df_band[ "SellExit" ]),
			max(df_band[ "Price" ])
		)
		min_px = min(
			min(df_band[ "BuyEntry" ]),
			min(df_band[ "BuyExit" ]),
			min(df_band[ "SellEntry" ]),
			min(df_band[ "SellExit" ]),
			min(df_band[ "Price" ])
		)

		# x轴
		index_longer = pd.DataFrame()
		for i_strategy_traderA in df_band[ "Strategy_TraderA" ].unique().tolist():
			i_index = df_band.loc[ df_band[ "Strategy_TraderA" ] == i_strategy_traderA, : ].index
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
		for i_strategy_traderA in df_band[ "Strategy_TraderA" ].unique().tolist():
			df_band_i = df_band.loc[ df_band[ "Strategy_TraderA" ] == i_strategy_traderA, : ]
			df_trader_price = df_band_i.loc[ :, [ 'Price', 'Ticker' ] ]
			strategy_name = i_strategy_traderA.split("_")[ 0 ]
			list_ticker_name = list(df_band_i[ 'Ticker' ].unique())

			line_band = Line()

			line_legend_top_position_str = "%s%%" % str(int(line_legend_top_position))
			line_legend_top_position += 5

			for i_band in [ "BuyEntry", "BuyExit", "SellEntry", "SellExit" ]:
				series_band = df_band_i[ i_band ]
				line_band.add(
					"%s-%s" % (strategy_name, i_band),
					x_axis=series_band.index.tolist(),
					y_axis=series_band.tolist(),
					yaxis_max=max_px,
					yaxis_min=min_px,
					xaxis_max=index_longer_max,
					xaxis_min=index_longer_min,
					is_xaxis_show=False,
					is_datazoom_show=True,
					datazoom_xaxis_index=[ 0, 1, 2 ],
					legend_top=line_legend_top_position_str
				)

			grid.add(
				line_band,
				grid_top=gird_top_str
			)

			# 选择时间周期更长的MKP
			if len(list_ticker_name) > len(list_ticker_name_longer):
				list_ticker_name_longer = list_ticker_name
				df_trader_price_longer = df_trader_price
			if len(df_trader_price) > len(df_trader_price_longer) and \
					len(list_ticker_name) == len(list_ticker_name_longer):
				df_trader_price_longer = df_trader_price

		# 画MKP
		line_legend_top_position_str = "%s%%" % str(int(line_legend_top_position))
		if len(df_trader_price_longer) > 0:
			line_mkp.add(
				"%s" % list(df_trader_price_longer[ "Ticker" ].unique())[ 0 ],
				x_axis=df_trader_price_longer.index.tolist(),
				y_axis=df_trader_price_longer[ 'Price' ].tolist(),
				yaxis_max=max_px,
				yaxis_min=min_px,
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
