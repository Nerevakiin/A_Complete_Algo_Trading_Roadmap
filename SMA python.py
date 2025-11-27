#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class SMABacktester():
    def __init__(self, symbol, SMA_S, SMA_L, start, end):
        self.symbol = symbol
        self.SMA_S = SMA_S
        self.SMA_L = SMA_L
        self.start = start
        self.end = end
        self.results = None
        self.data = None # Initialize data attribute
        self.get_data() # Call get_data to populate self.data

    def get_data(self):
        # Download the full DataFrame and assign it directly to 'data'
        data = yf.download(self.symbol, start=self.start, end=self.end)

        # --- THE PROBLEMATIC LINE IS REMOVED ---
        # data = df.Close.to_frame() # THIS IS GONE

        # Now, add new columns directly to the 'data' DataFrame
        data["returns"] = np.log(data.Close.div(data.Close.shift(1)))
        data["SMA_S"] = data.Close.rolling(self.SMA_S).mean()
        data["SMA_L"] = data.Close.rolling(self.SMA_L).mean()
        data.dropna(inplace=True)

        # Store the prepared data in the instance variable 'self.data'
        self.data = data

        # This return is optional as the main goal is to set self.data
        # but we'll leave it in case you use it elsewhere.
        return data

    def test_results(self):
        # Make sure data exists before proceeding
        if self.data is None:
            print("No data to test. Please check get_data().")
            return

        # Use self.data (corrected from self.data2)
        data = self.data.copy() # No need for a second dropna() here
        data["position"] = np.where(data["SMA_S"] > data["SMA_L"], 1, -1)
        data["strategy"] = data["returns"] * data.position.shift(1)
        data.dropna(inplace=True)
        data["returnsbh"] = data["returns"].cumsum().apply(np.exp)
        data["returnsstrategy"] = data["strategy"].cumsum().apply(np.exp)
        perf = data["returnsstrategy"].iloc[-1]
        outperf = perf - data["returnsbh"].iloc[-1]
        self.results = data

        # These lines were in the original but not used by the return statement
        # ret = np.exp(data["strategy"].sum())
        # std = data["strategy"].std() * np.sqrt(252)

        return round(perf, 6), round(outperf, 6)

    def plot_results(self):
        if self.results is None:
            print("Run the test please (call test_results() first).")
        else:
            title = "{} | SMA_S={} | SMA_L={}".format(self.symbol, self.SMA_S, self.SMA_L)
            self.results[["returnsbh", "returnsstrategy"]].plot(title=title, figsize=(12, 8))

