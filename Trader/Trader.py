import os
import pandas as pd
from Trader.Signal import Signal


class Trader:
	def __init__(self, file_path, trader_name, strategy_name, start_date, end_date, dt_round_level):
		self.data_path = file_path
		self.name = trader_name
		self.owner_strategy = strategy_name
		self.signal = Signal(strategy_name, trader_name, start_date, end_date, dt_round_level)
		self.pnl = pd.DataFrame()
		self.operate_mode = ""

	def get_target_position(self):
		path = self.data_path[ 'RawSignals' ]
		if os.path.isfile(path):
			self.signal.get_target_position(path)
		else:
			print(" This Trader has no RawSignal.csv and SIG_xx.csv")

	def get_band(self):
		path = self.data_path[ 'RawArbSignals' ]
		if os.path.isfile(path):
			self.signal.get_band(path)
		else:
			print(" This Trader has no RawArbSignal.csv and BAND_xx.csv")
