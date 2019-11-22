
import numpy as np


g_debug=False

class MatchNode(object):

	def __init__(self,space,history):
		self.space=space
		self.history=history

def generate_matches(state_space):
	#State Space is a 2D binary array where state_space[n,m] determines if player m can be assigned player n
	#Returns a 1D list of every players partner

	#Sort state space based on how many potential matches there are in ascending order
	space=np.array(state_space) #state space as a numpy array
	player_sort=np.argsort(np.sum(space,1)) # The player indices sorted by number of matches
	sorted_space=space[player_sort,:]
	
	stack=[] #Stack to holds states 
	decision_history=[] #History of choices
	tree_depth=0 #How far down the tree gone
	max_tree_depth=sorted_space.shape[0]

	while tree_depth<max_tree_depth:
		if np.in1d(np.sum(sorted_space,1),0).any():	#if a zero exists for matches for a player (aka this branch does not have a valid solution)
			if g_debug:
				print("Current Path has no solution, reverting")

			tree_depth-=1		#Decrement tree depth because we have to revert to an old state
			try:
				sorted_space=stack.pop(-1)	# Try to Pop the node off the stack
			except IndexError as e: # the stack is empty, meaning there's no valid solution
				raise ValueError("Provided state space has no solution, check your parameters")
			sorted_space[tree_depth,decision_history[-1]]=0	#Delete this branch from space because it's a bad solution
			decision_history.pop(-1) #remove the choice from history
		else:
			#pick one to match to and put unmodified space and decision on stack
			branch=np.random.choice(np.nonzero(sorted_space[tree_depth,:])[0])
			decision_history.append(branch)

			stack.append(np.copy(sorted_space)) #have to copy a new object to the stack and not a reference
			
			sorted_space[tree_depth+1:,branch]=0 #Modify space based on choice
			tree_depth+=1	#increment tree depth

		if g_debug:
			print("tree Depth:\t{}".format(tree_depth))
			print("Match History:\t{}".format(decision_history))
			print("Current State Space:\t")
			print(sorted_space)
	return decision_history[player_sort]

def main():
	state_space=[
				[0,1,0,0,0],
				[1,1,1,0,0],
				[0,0,0,1,1],
				[1,1,0,0,0],
				[1,0,1,1,0]
				]
	try:
		player_matches=generate_matches(state_space)
		print(player_matches)
	except ValueError as e:
		print("there is no valid solution for this space, exiting")

if __name__=='__main__':
	main()