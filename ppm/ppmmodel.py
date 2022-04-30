import ppm.arithmeticcoding as arithmeticcoding


class PpmModel:
	
	def __init__(self, order, symbol_limit, escape_symbol):
		if order < -1 or symbol_limit <= 0 or not (0 <= escape_symbol < symbol_limit):
			raise ValueError()
		self.model_order = order
		self.symbol_limit = symbol_limit
		self.escape_symbol = escape_symbol
		
		if order >= 0:
			self.root_context = PpmModel.Context(symbol_limit, order >= 1)
			self.root_context.frequencies.increment(escape_symbol)
		else:
			self.root_context = None
		self.order_minus1_freqs = arithmeticcoding.FlatFrequencyTable(symbol_limit)

	def increment_contexts(self, history, symbol):
		if self.model_order == -1:
			return
		if len(history) > self.model_order or not (0 <= symbol < self.symbol_limit):
			raise ValueError()
		
		ctx = self.root_context
		ctx.frequencies.increment(symbol)
		for (i, sym) in enumerate(history):
			subctxs = ctx.subcontexts
			assert subctxs is not None
			
			if subctxs[sym] is None:
				subctxs[sym] = PpmModel.Context(self.symbol_limit, i + 1 < self.model_order)
				subctxs[sym].frequencies.increment(self.escape_symbol)
			ctx = subctxs[sym]
			ctx.frequencies.increment(symbol)

	# Helper structure
	class Context:
		
		def __init__(self, symbols, hassubctx):
			self.frequencies = arithmeticcoding.SimpleFrequencyTable([0] * symbols)
			self.subcontexts = ([None] * symbols) if hassubctx else None
