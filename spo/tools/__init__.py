# -- encoding: UTF-8 --
import logging


class Tool(object):
	tool_name = None

	def __init__(self):
		self.log = logging.getLogger(self.__class__.__name__)

	@classmethod
	def populate_parser(cls, parser):
		pass

	def run(self, **kwargs):
		raise NotImplementedError("Not implemented.")