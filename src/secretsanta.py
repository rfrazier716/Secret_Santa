
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
	ENCODED_PLAYER_WIDTH=7	#how many bits are designated for player indices
	STACK_DIVIDER=0x1<<(2*ENCODED_PLAYER_WIDTH+1)	#Value written to stack to tell program to stop pulling

	def __init__(self,mutual_exclusion:True):
		self.mutual_exclusion=mutual_exclusion
		self.players=[] #List of the players

	def n_players(self):
		#Returns the number of players in the game
		return len(self.players)

	def load_players(self,player_list_file):
		self.players=[1,2,3,4,5]
		self.build_target_matrix()
		pass
		#TODO: make it load the players from a .json file
		#Also call the "build_target_matrix" function
	
	def build_target_matrix(self):
		#
		self.target_matrix=np.array([
				[0,1,0,1,0],
				[1,0,1,0,0],
				[0,0,0,1,1],
				[1,1,0,0,1],
				[1,0,1,1,0]
				])

	def encode_index(self,index):
		#accepts a tuple that is the row column value
		return (index[0]<<(self.ENCODED_PLAYER_WIDTH+1))+index[1]

	def decode_index(self,encoded_index):
		#accepts a 16 bit number and returns a tuple of (row,column)
		row=(encoded_index)>>(self.ENCODED_PLAYER_WIDTH+1)
		column=(encoded_index & ((1<<(self.ENCODED_PLAYER_WIDTH+1))-1))
		return row,column

	def assign_match(self,player,target):
		self.target_matrix[player,target]=0	#Set match to zero in target matrix
		
		#Write matched player to stack
		stack_value=self.encode_index((player,target))	
		self.stack.append(stack_value)	
		self.stack.append(self.STACK_DIVIDER)	#Write stack divider value

		#Update target matrix so no other players can be assigned the same target
		for j in range(player+1,self.n_players()): 
			if self.target_matrix[j,target]==1: #check if index is even a potential match
				
				#encode and write to stack
				stack_value=self.encode_index((j,target))
				self.stack.append(stack_value)

				self.target_matrix[j,target]=0	#set to zero in target matrix

	def undo_last_match(self):
		pass
		finished=False
		while not finished:
			stack_value=self.stack.pop(-1)
			if stack_value==self.STACK_DIVIDER:	
				#If we pull off a divider, stop pulling values
				finished=True
			else:
				#convert the value to a row column pair and write a 1 to that value in the target matrix
				row,column=self.decode_index(stack_value)
				self.target_matrix[row,column]=1


	def print_stack(self):
		for val in self.stack:
			print("{:04X}".format(val))

	def match_all_players(self):
		#returns a list of all matches such that player[n] is matched to player[list[n]]
		
		#Sort target matrix from least to greatest number of potential matches
		player_sort_indices=np.argsort(np.sum(self.target_matrix,1)) # The player indices sorted by number of matches
		self.target_matrix=self.target_matrix[player_sort_indices,:] #Rearrange the target matrix from fewest to largest matches
		player_to_match=0 #which player is currently being assigned a target
		match_list=[]	#List that keeps track of who matched with who, needs to be reordered after all matches are assigned
		self.stack=[]	#empty the stack
		
		while player_to_match<self.n_players():
			#Check if a valid solution space still exists
			if np.in1d(np.sum(self.target_matrix[player_to_match:],1),0).any():	#if the sum of options for any remaining players is zero
				#Solution space is no longer valid, revert to a previous choice
				match_list.pop(-1)
				self.undo_last_match()
				player_to_match-=1
			else:
				target=np.random.choice(np.nonzero(self.target_matrix[player_to_match,:])[0]) #Randomly pick a target for the current player based on options in target matrix
				self.assign_match(player_to_match,target) #Assign a new match
				match_list.append(target)
				player_to_match+=1

			#print(self.target_matrix)
			#print("player:{}\tCurrent Stack".format(player_to_match))
			#self.print_stack()
			#print("")

		sorted_matches=[match_list[index] for index in player_sort_indices] #change the match list back to its original order
		return sorted_matches #return the list of matches

def import_player_list(file):
	pass

def main():
	player_list_file=Path(sys.argv[0]) / 'private' / 'player_list.json'
	players=import_player_list(player_list_file)

if __name__=='__main__':
	main()