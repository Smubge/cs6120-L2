import json
import sys

class Block:
	def __init__(self, idx, instrs):
		self.idx = idx
		self.instrs = instrs
		self.edges = []

	def label(self):
		if self.instrs and "labels" in self.instrs[0]:
			return self.instrs[0]["labels"]
		return None
	
	def last(self):
		if self.instrs:
			return self.instrs[-1]
		return None

	def add_edge(self, target):
		if target not in self.edges:
			self.edges.append(target)
	
	def __str__(self):
		return f"Block(idx={self.idx}, label={self.label}, edges = {self.edges} )"          

with open(sys.argv[1], 'r') as file:
	instrs = json.load(file)

blocks = []
block = []
selfIdx = 0

# creating basic blocks implementation
for func in instrs["functions"]:
    if "instrs" in func:
        for instr in func["instrs"]:  # loop over instructions in the function
            if "label" in instr:
                b0 = Block("v" + str(selfIdx), block)
                selfIdx += 1
                blocks.append(b0)
                block = []
                block.append(instr)
            elif "op" in instr:
                if instr["op"] == "br" or instr["op"] == "jmp":
                    b1 = Block("v" + str(selfIdx), block)
                    selfIdx += 1
                    blocks.append(b1)
                    block = []
                    block.append(instr)
                else:
                    selfIdx += 1
                    block.append(instr)
if block:
    b2 = Block("v" + str(selfIdx), block)
    selfIdx += 1
    blocks.append(b2)
    block = []

cfg = {}
# cfg implementation
"""
basic blocks:
* ends with a terminator
* starts with a label
* has neither
* has both
"""

'''
for b in blocks:
	last = b[-1] // last instr in block, doesn't work if blocks empty
	if last is "jmp":
		cfg[b.name] = [last.dest] // assume each block has label/id
	else if last is "br":
		cfg[b.name] = [last.true_label, last.false_label]
	else:
		cfg[b.name] = [(b + 1).name] // next block in the list
'''
for b in blocks:
	last = b.last() # last instr in block, doesn't work if blocks empty
	if last is not None:
		if "op" in last:
			if last["op"] == "jmp":
				if "labels" in last: 
					cfg[b.idx] = last["labels"]
				else:
					cfg[b.idx] = [last["dest"]]
			elif last["op"] == "br":
				cfg[b.idx] = [last["labels"][0], last["labels"][1]]
		elif "dest" not in last and "labels" not in last:
			cfg[b.idx] = []
		else:
			text = b.idx[0]
			num = b.idx[1]
			new_num = str(int(num) + 1)
			new_idx = text + new_num
			cfg[b.idx] = [new_idx]

print(cfg)
		