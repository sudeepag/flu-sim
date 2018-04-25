"""
Simple Logging class with util functions for printing output.
"""
from Constants import TIME
class Logger:

	def __init__(self, n_iterations):
		self._log = [[] for _ in range(n_iterations)]

	def log(self, ts, text):
		self._log[ts].append(text)

	def print_log(self, ts):
		for l in self._log[ts]:
			print(l)


logger = Logger(TIME)