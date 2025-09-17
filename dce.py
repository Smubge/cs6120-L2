"""
This script takes in a Bril JSON file and outputs a new Bril program 
with dead code eliminated
"""

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

	def labels(self):
		if self.instrs and "labels" in self.instrs[0]:
			return self.instrs[0]["labels"]
		return None

	def label(self):
		if self.instrs and "label" in self.instrs[0]:
			return self.instrs[0]["label"]
		return None

	def last(self):
		if self.instrs:
			return self.instrs[-1]
		return None

	def get_args(self):
		if self.instrs and "args" in self.instrs[0]:
			return self.instrs[0]["args"]
		return None

	def add_edge(self, target):
		if target not in self.edges:
			self.edges.append(target)
	
	def __str__(self):
		return f"Block(idx={self.idx}, label={self.label()}, edges = {self.edges} )"          

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

used_labels = {}

def get_unique_block_name(self,lbl):
    if self: 
        first = self[0]
        if "label" in first:
            l = first["label"]
            if l in used_labels:
                used_labels[l] += 1
                return l + "_" + used_labels[l]
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
                b0 = Block(get_unique_block_name(block, instr["label"]), block)
                selfIdx += 1
                blocks.append(b0)
                block = []
                block.append(instr)
            elif "op" in instr:
                if instr["op"] == "br" or instr["op"] == "jmp" or instr["op"] == "ret":
                    b1 = Block(get_unique_block_name(block, ""), block)
                    selfIdx += 1
                    block.append(instr)
                    blocks.append(b1)
                    block = []
                else:
                    selfIdx += 1
                    block.append(instr)
if block:
    b2 = Block(get_unique_block_name(block, ""), block)
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

def print_basic_blocks():
    for b in blocks:
        print(b)

print_basic_blocks()
print ("Testing dce here")
def local_dce(self, block):
    alive = {}
    for instr in block.instrs:
        args = instr.get_args
        if args is not None:
            for arg in args:
                alive.insert(arg)
        
    for instr in block.instrs:
        if "dest" in instr:
            if instr["dest"] not in alive:
                block.instrs.remove(instr)