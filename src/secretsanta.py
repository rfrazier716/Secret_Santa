
import numpy as np
import sys
from pathlib import Path


g_debug=False

class Player(object):
	def __init__(self,first_name,last_name,email,blacklist):
		self.first_name
		self.last_name
		self.name=self.first_name+" "+self.last_name
		self.email=email
		self.blacklist=blacklist
		self.target=""

class MatchEngine():
	def __init__(self,mutual_exclusion:True):
		self.mutual_exclusion=mutual_exclusion
		self.stack=[]	#Stack that's used for spanning the choice matrix
		self.players=[] #List of the players

	def n_players(self):
		#Returns the number of players in the game
		return len(self.players)

	def load_players(self,player_list_file):
		self.build_target_matrix()
		pass
		#TODO: make it load the players from a .json file
		#Also call the "build_target_matrix" function
	
	def build_target_matrix(self):
		#
		self.target_matrix=np.array([
				[0,1,0,0,0],
				[1,1,1,0,0],
				[0,0,0,1,1],
				[1,1,0,0,0],
				[1,0,1,1,0]
				])

	def push_index_to_stack(self,row,column):
		# pushes a matrix coordinate onto the stack
		self.stack.append(row)
		self.stack.append(column)
		pass

	def pull_index_from_stack(self):
		#pulls a matrix coordinate off the stack and returns it as row, column
		column=self.stack.pop(-1)
		row=self.stack.pop(-1)
		return row,column

	def null_potential_match(self,player,match):
		#writes a zero to the target matrix to remove the chancce that a player 
		pass

	def assign_match(self,player):
		match=np.random.choice(np.nonzero(self.target_matrix[player,:])[0]) #Choose a match randomly based on the possible pairings
		#write that stack with a zero so that if it gets pulled the option in the tree is deleted

		return match #return the match





	def undo_last_match(self):
		indices_to_revert=stack.pop(-1) #The most recent stack value should say how many indices were written
		for _ in range(indices_to_revert):
			col=stack.pop(-1)	#Pull the row off the stack
			row=stack.pop(-1)	#Pull the column off the stack
			self.target_matrix[row,col]=1 #Revert the XYCoord to it's last state


	def match_all_players(self):
		#Return a tuple of  [[player_0,target_0],...,[player_n,target_n]] form
		#Sort target matrix from least to greatest number of potential matches
		player_sort_indices=np.argsort(np.sum(space,1)) # The player indices sorted by number of matches
		self.target_matrix=self.target_matrix[player_sort_indices,:] #Rearrange the target matrix from fewest to largest matches
		player_to_match=0 #which player is currently being assigned a target
		match_list=[]
		
		while player_to_match<self.n_players():
			#Check if a valid solution space still exists
			if np.in1d(np.sum(sorted_space,1),0).any():	
				#Solution space is no longer valid, revert to a previous choice
				self.undo_last_match()
			else:
				self.assign_match()
			#If it does exist assign a new match and push all changes to the queue



def generate_matches(state_space):
	#State Space is a 2D binary array where state_space[n,m] determines if player m can be assigned player n
	#Returns a 1D list of every players partner

	#Algorithm uses a stack with following chunks written at any point

	#Sort state space based on how many potential matches there are in ascending order
	space=np.array(state_space) #state space as a numpy array
	player_sort=np.argsort(np.sum(space,1)) # The player indices sorted by number of matches
	sorted_space=space[player_sort,:]
	
	stack=[] #Stack to holds states 
	tree_depth=0 #How far down the tree gone
	max_tree_depth=sorted_space.shape[0]

	while tree_depth<max_tree_depth:
		if np.in1d(np.sum(sorted_space,1),0).any():	#if a zero exists for matches for a player (aka this branch does not have a valid solution)
			if g_debug:
				print("Current Path has no solution, reverting")

			try:
				failed_branch=stack.pop(-1)	# Try to Pop the node off the stack
				sorted_space[tree_depth:,failed_branch]=1
			except IndexError as e: # the stack is empty, meaning there's no valid solution
				raise ValueError("Provided state space has no solution, check your parameters")

			sorted_space[tree_depth,decision_history[-1]]=0	#Delete this branch from space because it's a bad solution
			decision_history.pop(-1) #remove the choice from history
		else:
			#pick one to match to and put unmodified space and decision on stack
			branch=np.random.choice(np.nonzero(sorted_space[tree_depth,:])[0])
			stack.append(branch) # Append the choice to the stack			
			sorted_space[tree_depth+1:,branch]=0 #Modify space based on choice
			tree_depth+=1	#increment tree depth

		if g_debug:
			print("tree Depth:\t{}".format(tree_depth))
			print("Match History:\t{}".format(decision_history))
			print("Current State Space:\t")
			print(sorted_space)
	return decision_history[player_sort]

def main():
	engine=MatchEngine(False)
	engine.load_players(1)
	print(engine.target_matrix)

if __name__=='__main__':
	main()