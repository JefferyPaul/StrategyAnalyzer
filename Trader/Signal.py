from datetime import *
import pandas as pd

'''
	数据格式
	band, df
	[
	"DateTime", 
	"BuyEntry", "BuyExit", "SellEntry", "SellExit",
	"Close1", "Close2",
	"Ticker1", "Ticker2",
	"Ticker", "Price"
	]
'''


class Signal:
	def __init__(self, strategy_name, trader_name, start_date, end_date, dt_round_level):
		self.owner_trader = trader_name
		self.owner_strategy = strategy_name

		self.target_position = pd.DataFrame()
		self.std_target_position = pd.DataFrame()
		self.band = pd.DataFrame()
		self.price = pd.DataFrame()

		self.start_date = start_date
		self.end_date = end_date
		self.dt_round_level = dt_round_level

	def get_target_position(self, file_path):
		# RawSignals.csv / SIG_xxx.csv
		with open(file_path) as f:
			df = pd.read_csv(f)
			df["DateTime"] = df["Date"] + " " + df["Time"]
			df["DateTime"] = pd.to_datetime(df["DateTime"], format="%Y-%m-%d %H:%M:%S").dt.round(self.dt_round_level)
			df = df[self.start_date < df["DateTime"]]
			df = df[df["DateTime"] < self.end_date]

		df["Strategy_TraderA"] = "%s-%s" % (self.owner_strategy, self.owner_trader)
		df["TargetPosition"] = df["TargetPosition"] / df["InitX"]
		df = df.loc[
		     :,
		     ["DateTime",
		      "Ticker",
		      "Strategy_TraderA",
		      "TargetPosition",
		      "Price"]
		     ]
		# df.index = df["DateTime"]

		self.target_position = df
		self.cal_std_target_position()
		self.cal_pair_price()

	def get_band(self, file_path):
		# RawArbSignals.csv / BAND_xxx.csv
		try:
			with open(file_path, 'r', encoding='GB2312') as f:
				df = pd.read_csv(f, index_col=None)
				df["DateTime"] = df["Date"] + " " + df["Time"]
				df["DateTime"] = pd.to_datetime(df["DateTime"], format=r"%Y/%m/%d %H:%M:%S").dt.round(
					self.dt_round_level)
				df = df.loc[self.start_date < df["DateTime"], :]
				df = df.loc[df["DateTime"] < self.end_date, :]
				df['Price'] = df["Close1"] / df["Close2"]
				df["Ticker"] = "%s / %s" % (df["Ticker1"].tolist()[0], df["Ticker2"].tolist()[0])
				df["Strategy_TraderA"] = "%s-%s" % (self.owner_strategy, self.owner_trader)
				df = df.loc[
				     :,
				     ["DateTime",
				      "Strategy_TraderA",
				      "Ticker",
				      "BuyEntry",
				      "BuyExit",
				      "SellEntry",
				      "SellExit",
				      "Price"
				      ]
				     ]
			# df.index = df["DateTime"]
			self.band = df
		except:
			pass

	def cal_std_target_position(self):
		l = []
		for i_ticker in self.target_position["Ticker"].unique().tolist():
			df = self.target_position.loc[self.target_position["Ticker"] == i_ticker, :]
			df.loc[:, "TargetPosition"] = df.loc[:, "TargetPosition"] / max(abs(df["TargetPosition"]))
			l.append(df)
		try:
			df = pd.DataFrame(pd.concat(l, ignore_index=True))
			# df.index = df["DateTime"]
			df = df.loc[
			     :,
			     ["DateTime",
			      "Ticker",
			      "Strategy_TraderA",
			      "TargetPosition",
			      "Price"]
			     ]
		except:
			df = pd.DataFrame()
		self.std_target_position = df

	def cal_pair_price(self):
		df = self.target_position
		if len(df["Ticker"].unique().tolist()) > 1:
			list_ticker_name = df["Ticker"].unique().tolist()
			df_price_pivot = pd.pivot_table(
				df,
				index="DateTime",
				columns="Ticker",
				values="Price"
			)
			df_price_pivot['Price'] = df_price_pivot[list_ticker_name[0]] / df_price_pivot[
				list_ticker_name[1]]

			df_price = df_price_pivot[["Price"]]
			df_price = df_price.dropna()

			df_price.loc[:, "Ticker"] = "%s / %s" % (list_ticker_name[0], list_ticker_name[1])
			df_price["DateTime"] = df_price.index
			df_price["Strategy_TraderA"] = df["Strategy_TraderA"].unique().tolist()[0]
			self.price = df_price
		else:
			self.price = df.loc[
			             :,
			             ["DateTime",
			              "Ticker",
			              "Strategy_TraderA",
			              "Price"]
			             ]
