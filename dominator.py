
"""
Control Flow Graph!
Jonathan Brown and Cynthia Shao

This script takes in a Bril json file and outputs the 
corresponding control flow graph in a edge list format.
"""
from enum import Enum
import json
import sys
from collections import deque
     
class Block:
	def __init__(self, idx, instrs, is_func_header):
		self.idx = idx
		self.instrs = instrs
		self.edges = []
		self.is_header = is_func_header

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
with open(sys.argv[1], 'r') as file:
	instrs = json.load(file)
# instrs = json.load(sys.stdin)

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
func_headers = []
is_func_header = False
# creating basic blocks implementation
for func in instrs["functions"]:
    if "instrs" in func:
        for (i, instr) in enumerate(func["instrs"]):  # loop over instructions in the function
            if i == 0:
                is_func_header = True
            if "label" in instr:
                b0 = Block(get_block_name(block, ""), block, is_func_header)
                if is_func_header == True:
                    b0 = Block("f" + func["name"], block, is_func_header)
                is_func_header = False 
                selfIdx += 1
                blocks.append(b0)
                block = []
                block.append(instr)
            elif "op" in instr:
                if instr["op"] == "br" or instr["op"] == "jmp" or instr["op"] == "ret":
                    b1 = Block(get_block_name(block, ""), block, is_func_header)
                    if is_func_header == True:
                        b1 = Block("f" + func["name"], block, is_func_header)
                    is_func_header = False
                    selfIdx += 1
                    block.append(instr)
                    blocks.append(b1)
                    block = []
                else:
                    selfIdx += 1
                    block.append(instr)
        if block:
            b2 = Block(get_block_name(block, ""), block, is_func_header)
            if is_func_header == True:
                b2 = Block("f" + func["name"], block, is_func_header)
            is_func_header = False
            selfIdx += 1
            blocks.append(b2)
            block = []

# for (i, b) in enumerate(blocks): 
#     print(f"block unedited {i} : {b}")
    
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
			cfg[b.idx] = [probe_next(b.idx)]
		else:
			cfg[b.idx] = [probe_next(b.idx)]
	else:
		cfg[b.idx] = [probe_next(b.idx)]

print(f"cfg: {cfg} \n")
cleanup_arr = []
for (i, block) in enumerate(blocks):
    if block.idx != "":
         cleanup_arr.append(block)
blocks = cleanup_arr


# for (i, b) in enumerate(blocks): #Cleaned up arr
    # print(f"block edited {i} : {b}")


for block in blocks:
    if block.is_header:
        func_headers.append(block)

def probe_next_func_cfg(block):
    found = False
    for (i,b) in enumerate(blocks):
        if found: 
            if b.idx != block and b.is_header == False:
                return [b.idx]
        if (b.idx) == block:
            found = True
    return []


func_cfg = {}
for b in blocks:
	last = b.last() # last instr in block, doesn't work if blocks empty
	if last is not None:
		if "op" in last:
			if last["op"] == "jmp":
				if "labels" in last: 
					func_cfg[b.idx] = last["labels"]
				else:
					func_cfg[b.idx] = [last["dest"]]
			elif last["op"] == "br":
				func_cfg[b.idx] = [last["labels"][0], last["labels"][1]]    
			elif last["op"] == "ret":
				func_cfg[b.idx] = []
			elif "dest" not in last and "labels" not in last:
				func_cfg[b.idx] = []
			else:
				func_cfg[b.idx] = probe_next_func_cfg(b.idx)
		elif "dest" not in last and "labels" not in last:
			func_cfg[b.idx] = probe_next_func_cfg(b.idx)
		else:
			func_cfg[b.idx] = probe_next_func_cfg(b.idx)
	else:
		func_cfg[b.idx] = probe_next_func_cfg(b.idx)
idx_to_func = {}
func_idx = None
func_to_idx = {}
func_idx_list = []
for (i,b) in enumerate(blocks):
    if b.is_header:
        func_to_idx[b.idx] = func_idx_list
        func_idx_list = []
    else:
        func_idx_list.append(b.idx)
# print(f"func_to_idx: {func_to_idx}")
# for (idx, func_list) in func_to_idx.items():
#     for block in func_list:
#         print(idx)


dom = {}
idx_set = []
for b in blocks:
     idx_set.append(b.idx)
idx_set = set(idx_set)

for b in blocks:
    if b.idx == blocks[0].idx:
        dom[b.idx] = {b.idx}
    else:
        dom[b.idx] = idx_set.copy()


def find_pred(b_idx, preds, dom):
    if not preds[b_idx]:
        return set()
    result = dom[preds[b_idx][0]].copy() #set intersction of preds like stated in lecture 
    for p in preds[b_idx][1:]:
        result = result & dom[p]
    return result
             
def build_preds(cfg): #TODO: check correctness on this? (not entirely sure)
    preds = {b: [] for b in cfg}
    for src, succs in cfg.items():
        if (succs == "for.body"):
             print("hi")
        for s in succs:
            if s in preds:
                preds[s].append(src)
            else:
                preds[s] = [src]
    return preds

preds = build_preds(func_cfg)
print(f"predecess: {preds} \n")
while True:
    prev_dom = {}
    for k in dom:
        v = dom[k]
        temp = set(v)
        prev_dom[k] = temp
    for b in blocks:
        if b.idx == blocks[0].idx:
            continue
        dom[b.idx] = {b.idx}.union(find_pred(b.idx, preds, dom))
    if dom == prev_dom:
        break
print(f"dom: {dom} \n")
sorted_dom = {k: sorted(list(v)) for k, v in sorted(dom.items())}
# print(sorted_dom)
print(f"func_cfg: {func_cfg} \n")
print(f"cfg: {cfg} \n")
def traverse_cfg(cfg, func_header, paths):
    """
    Return all paths from the source to every block in the cfg.

    cfg: a dictionary representing the cfg. keys are block names, 
    values are the successors of this block
    block: block.idx

    returns `paths` a dictionary where k: block in cfg 
    v: a list of all possible paths to block k
    """
    
    # Track visited (node, predecessor) pairs to avoid infinite loops
    visited_pairs = set()
    
    # Queue stores (current_node, path_to_current_node)
    queue = deque()
    
    # The source in the cfg is blocks[0]
    source = func_header
    
    # Initialize with source node (no predecessor, so use None)
    queue.append((source, [source]))
    visited_pairs.add((source, None))
    paths[source] = [[source]]
    
    while queue:
        curr_node, curr_path = queue.popleft()
        
        # Get successors of current node
        if curr_node in cfg:
            for successor in cfg[curr_node]:
                # Check if this (successor, predecessor) pair is unique
                pair = (successor, curr_node)
                if pair not in visited_pairs:
                    visited_pairs.add(pair)
                    
                    # Create new path by extending current path
                    new_path = curr_path + [successor]
                    
                    # Add to paths dictionary
                    if successor not in paths:
                        paths[successor] = []
                    paths[successor].append(new_path)
                    
                    # Add to queue for further exploration
                    queue.append((successor, new_path))
    

def test_dom():
    """
    this function verifies the generated dominators

    given blocks A and B, we want to verify that A dominates B by:
    enumerating all possible paths to B
    checking if A exists on all possible paths to B before B occurs.

    returns true/false if the given dominator set is correct given the cfg 
    """
    
    paths = {}
    for f in func_headers:
        traverse_cfg(cfg, f.idx, paths)
        # traverse_cfg(func_cfg, f.idx, paths)
    
    for block in dom.keys():  # For each block
        for dominator in dom[block]:  # For each claimed dominator of this block
            if dominator == block:  # Skip self-domination (always true)
                continue
                
            # Get all paths to the block being dominated
            if block not in paths:
                print(f"No paths found to block {block}")
                continue
                
            block_paths = paths[block]
            
            # Check if dominator appears in ALL paths to block, before block
            for path in block_paths:
                # Find first occurrence of the dominated block
                try:
                    first_block_idx = path.index(block)
                except ValueError:
                    print(f"Block {block} not found in its own path: {path}")
                    return False
                
                # Check if dominator appears before the first occurrence of block
                path_before_block = path[:first_block_idx]
                if dominator not in path_before_block:
                    print(f"Dominator {dominator} does not dominate {block}")
                    print(f"Path: {path}, dominator not in prefix: {path_before_block}")
                    return False
    
    # print("All dominators verified successfully!")
    return True

correct = test_dom()

if not correct:
    sys.exit()