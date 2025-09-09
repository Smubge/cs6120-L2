"""
Control Flow Graph!
Jonathan Brown and Cynthia Shao

This script takes in a Bril json file and outputs the 
corresponding control flow graph in a edge list format.
"""

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

def split_func_calls(funcs): #get funcy
    res = ""
    for (i,func) in enumerate(funcs):
        if i < (len(funcs) - 1):
            res += func + ", "
        else:
            res += func
    print(res)
    return res

def get_block_name(self,lbl):
    if self: 
        first = self[0]
        if "label" in first:
            return first["label"]
        elif "dest" in first:
            return first["dest"]
        elif "funcs" in first:
            return split_func_calls(first["funcs"])
        else:
            return first["op"]
    else:
        return lbl

# creating basic blocks implementation
for func in instrs["functions"]:
    if "instrs" in func:
        for instr in func["instrs"]:  # loop over instructions in the function
            if "label" in instr:
                b0 = Block(get_block_name(block, instr["label"]), block)
                selfIdx += 1
                blocks.append(b0)
                block = []
                block.append(instr)
            elif "op" in instr:
                if instr["op"] == "br" or instr["op"] == "jmp" or instr["op"] == "ret":
                    b1 = Block(get_block_name(block, ""), block)
                    selfIdx += 1
                    block.append(instr)
                    blocks.append(b1)
                    block = []
                else:
                    selfIdx += 1
                    block.append(instr)
if block:
    b2 = Block(get_block_name(block, ""), block)
    selfIdx += 1
    blocks.append(b2)
    block = []
    
def probe_next(block):
    found = False
    for (i,b) in enumerate(blocks):
        if found: 
            if b.idx != block:
                return b.idx
        if (b.idx) == block:
            found = True

# building the control flow graph edge list!
cfg = {}
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
			elif last["op"] == "ret":
				cfg[b.idx] = []
			elif "dest" not in last and "labels" not in last:
				cfg[b.idx] = []
			else:
				cfg[b.idx] = [probe_next(b.idx)]
		elif "dest" not in last and "labels" not in last:
			cfg[b.idx] = []
		else:
			cfg[b.idx] = [probe_next(b.idx)]

print(cfg)
		