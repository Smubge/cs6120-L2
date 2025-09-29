
"""
Control Flow Graph!
Jonathan Brown and Cynthia Shao

This script takes in a Bril json file and outputs the 
corresponding control flow graph in a edge list format.
"""
from enum import Enum
import json
import sys

class Table_Occ(Enum):
     IN_TABLE = 1
     NOT_IN_TABLE = 2
     REPLACE = 3
     PRINT_RET = 4
     DONT_USE = 5
     

commutative_instr = ["call", "add", "mul", "and", "or", "eq", "neq"]
#Make var a sort of enum, make var a str, and make idx a num
class LVN_Value:
    def __init__(self, instr, vars): #Instr = string, var1 is the variable index, var2 is the var index
        self.instr = instr 
        if instr in commutative_instr:
            sorted_vars = tuple(sorted(vars))
            self.vars = sorted_vars
        else:
            self.vars = vars
    #TODO: Watch out, subtraction needs the order kept, only for commutative properties, do some sort of checking for add, mul, etc, otherwise do nothing
        
    #TODO: Watch out, const values can be confused for actual vals
    def __eq__(self, other):
        if self.instr == other.instr:
            for (i, var) in enumerate(self.vars):
                for (j, var2) in enumerate(other.vars):
                    if i == j:
                        if type(var) is not type(var2) or var != var2:
                            return False 
            return True
        else:
            return False
    def __str__(self):
        return f"(Instr = {self.instr}, Value = ({self.vars}))"
    __repr__ = __str__

class LVN_Table:
    def __init__(self, idx, value, var):
        self.idx = idx
        self.value = value
        self.var = var 
    def __str__(self):
        return f"(Idx = {self.idx}, Value = {self.value}, Var = {self.var})"
    __repr__ = __str__


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
		return f"Block(idx={self.idx}, label={Block.label(self)}, edges = {self.edges} )"          
	__repr__ = __str__
# with open(sys.argv[1], 'r') as file:
# 	instrs = json.load(file)
instrs = json.load(sys.stdin)

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

         
cleanup_arr = []
for (i, block) in enumerate(blocks):
    if block.instrs:
         cleanup_arr.append(block)
blocks = cleanup_arr

live_in = {}
live_out = {}
for b in blocks:
     live_out[b.idx] = set()
     live_in[b.idx] = set()

use = {}
defs = {}
for b in blocks:
    use_block = set()
    def_block = set()
    for instr in b.instrs:
        if "args" in instr:
            for a in instr["args"]:
                if a not in def_block:
                    use_block.add(a)
        if "dest" in instr:
            def_block.add(instr["dest"])
    use[b.idx] = use_block
    defs[b.idx] = def_block

while True:
    #Set previous outputs
    prev_in = {}
    for k in live_in:
        v = live_in[k]
        temp = set(v)
        prev_in[k] = temp

    prev_out = {}
    for k in live_out:
        v = live_out[k]
        temp = set(v)
        prev_out[k] = temp

    new_out = {}
    for b in blocks:
        s = set()
        for succ in cfg.get(b.idx, []):
            if succ is None:
                continue
            s = s.union(prev_in.get(succ, set()))
        new_out[b.idx] = s

    new_in = {}
    for b in blocks:
        new_in[b.idx] = use[b.idx].union(new_out[b.idx] - defs[b.idx])
    live_in = new_in
    live_out = new_out
    if live_in == prev_in and live_out == prev_out:
        break

def live_print(s):
    if not s:
        return "∅"
    result = "{"
    for (i, var) in enumerate(sorted(s)):
        if i > 0:
            result += ", "
        result += var
    result += "}"
    return result

for b in blocks:
     print(f"Block: {b.idx}")
     print(f"In: {live_print(live_in[b.idx])}")
     print(f"Out: {live_print(live_out[b.idx])}")
