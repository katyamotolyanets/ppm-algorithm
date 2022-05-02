# 
# Decompression application using prediction by partial matching (PPM) with arithmetic coding
# 
# Usage: python ppm_decompress.py InputFile OutputFile

import sys
from ppm import arithmeticcoding, ppmmodel


# Must be at least -1 and match ppm_compress.py. Warning: Exponential memory usage at O(257^n).
MODEL_ORDER = 3


# Command line main application function.
def main(args):
	# Handle command line arguments
	if len(args) != 2:
		sys.exit("Usage: python ppm_decompress.py InputFile OutputFile")
	inputfile  = args[0]
	outputfile = args[1]
	
	# Perform file decompression
	with open(inputfile, "rb") as inp, open(outputfile, "wb") as out:
		bitin = arithmeticcoding.BitInputStream(inp)
		decompress(bitin, out)


def decompress(bitin, out):
	# Set up decoder and model. In this PPM model, symbol 256 represents EOF;
	# its frequency is 1 in the order -1 context but its frequency
	# is 0 in all other contexts (which have non-negative order).
	dec = arithmeticcoding.ArithmeticDecoder(32, bitin)
	model = ppmmodel.PpmModel(MODEL_ORDER, 257, 256)
	history = []
	
	while True:
		# Decode and write one byte
		symbol = decode_symbol(dec, model, history)
		if symbol == 256:  # EOF symbol
			break
		out.write(bytes((symbol,)))
		model.increment_contexts(history, symbol)
		
		if model.model_order >= 1:
			# Prepend current symbol, dropping oldest symbol if necessary
			if len(history) == model.model_order:
				history.pop()
			history.insert(0, symbol)


def decode_symbol(dec, model, history):
	# Try to use highest order context that exists based on the history suffix. When symbol 256
	# is consumed at a context at any non-negative order, it means "escape to the next lower order
	# with non-empty context". When symbol 256 is consumed at the order -1 context, it means "EOF".
	for order in reversed(range(len(history) + 1)):
		ctx = model.root_context
		for sym in history[ : order]:
			assert ctx.subcontexts is not None
			ctx = ctx.subcontexts[sym]
			if ctx is None:
				break
		else:  # ctx is not None
			symbol = dec.read(ctx.frequencies)
			if symbol < 256:
				return symbol
			# Else we read the context escape symbol, so continue decrementing the order
	# Logic for order = -1
	return dec.read(model.order_minus1_freqs)


# Main launcher
if __name__ == "__main__":
	main(sys.argv[1 : ])
