
import numpy as np
import sys
import json
from pathlib import Path
import gmailsmtp as gm


g_debug=False
g_software_version="1.0"

class Player(object):
	def __init__(self,first_name,last_name,email,**kwargs):
		self.first_name=first_name
		self.last_name=last_name
		self.name=self.first_name+" "+self.last_name
		self.email=email
		self.target=""

		#Additional Optional arguments
		self.whitelist=kwargs.get('whitelist',[])
		self.blacklist=kwargs.get('blacklist',[])

class MatchEngine():
	ENCODED_PLAYER_WIDTH=7	#how many bits are designated for player indices
	STACK_DIVIDER=0x1<<(2*ENCODED_PLAYER_WIDTH+1)	#Value written to stack to tell program to stop pulling

	def __init__(self,**kwargs):
		self.mutual_exclusion=kwargs.get('exclusion',False)	#If exclusion is set to players cannot be assigned each other
		self.players=[] #List of the players
		self.player_match_list=[]

	def n_players(self):
		#Returns the number of players in the game
		return len(self.players)

	def import_players(self,players):
		self.players=players #Load players
		self.build_target_matrix()	#build target_matrix from player list
	
	def build_target_matrix(self):
		self.target_matrix=np.ones(self.n_players(),dtype=int)-np.eye(self.n_players(),dtype=int)	#Make a matrix of 1's the size of the number of self.players but set it so no player can be assigned themselves
		player_names=[player.name for player in self.players]
		for row in range(len(self.players)):
			if not self.players[row].whitelist: #If a whitelist isn't defined build matrix based on blacklist
				for blacklisted_player in self.players[row].blacklist:
					try:
						column=player_names.index(blacklisted_player) #find the index of the blacklisted target in the list
						self.target_matrix[row,column]=0	#write a zero to that index in the target matrix
					except ValueError: #if the player could not be found, raise an error saying as much
						raise ValueError("Player in blacklist does not exist. Verify correct spelling")
			else:	#If a whitelist has been defined it overrides any blacklist preferences
				self.target_matrix[row,:]=0	#set target matrix to zero because only whitelisted players are allowed as a match
				for whitelisted_player in self.players[row].whitelist:
					try:
						column=player_names.index(whitelisted_player) #find the index of the whitelisted target in the list
						self.target_matrix[row,column]=1	#write a zero to that index in the target matrix
					except ValueError: #if the player could not be found, raise an error saying as much
						raise ValueError("Player in Whitelist does not exist. Verify correct spelling")

		return self.target_matrix

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

		#if mutual_exclusion flag is set modify matrix to target cannot be assigned player
		if self.mutual_exclusion:
			if self.target_matrix[target,player]==1:
				self.target_matrix[target,player]=0	#null out this option
				stack_value=self.encode_index((target,player))	#Push Value to stack
				self.stack.append(stack_value)

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

	def print_matches(self):
		for n in range(len(self.player_match_list)):
			print(self.players[n]+" was assigned "+self.players[self.player_match_list[n]])

	def print_stack(self):
		for val in self.stack:
			print("{:04X}".format(val))

	def match_all_players(self):		
		#Sort target matrix from least to greatest number of potential matches
		player_sort_indices=np.argsort(np.sum(self.target_matrix,1)) # The player indices sorted by number of matches
		self.target_matrix=self.target_matrix[player_sort_indices,:] #Rearrange rows by fewest to largest matches
		self.target_matrix=self.target_matrix[:,player_sort_indices] #Rearrange columns by fewest to largest matches
		#print(self.target_matrix)
		player_to_match=0 #which player is currently being assigned a target
		match_list=[]	#List that keeps track of who matched with who, needs to be reordered after all matches are assigned
		self.stack=[]	#empty the stack
		
		while player_to_match<self.n_players():
			#Check if a valid solution space still exists
			if np.in1d(np.sum(self.target_matrix[player_to_match:],1),0).any():	#if the sum of options for any remaining players is zero
				#Solution space is no longer valid, revert to a previous choice
				try:
					match_list.pop(-1)
				except IndexError:
					raise IndexError("Tried to pull from empty stack. Solution does not exist")
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
		self.player_match_list=[match_list[index] for index in player_sort_indices] #change the match list back to its original order
		for j in range(self.n_players()):
			self.players[player_sort_indices[j]].target=self.players[player_sort_indices[match_list[j]]].name
		return [(player.name,player.target) for player in self.players] #return the list of matches

def import_player_list(f_player_list):
	players=[]
	with open(f_player_list) as json_file:
		data=json.load(json_file)
		for entry in data:
			players.append(Player(
				entry.get('first_name'),
				entry.get('last_name'),
				entry.get('email'),
				blacklist=entry.get('blacklist',[]),
				whitelist=entry.get('whitelist',[])
				))
	return players

def print_targets(players):
	for player in players:
		print(player.name+" is assigned "+player.target)

def email_player_target(player,server):
	server.sendmail(
  	server.email_address, 
	player.email,
 	'''
 	Ho Ho Hello Santas!,
 	your target is below, let the give giving begin!

 	{}, You have been assigned: {}

 	-Fotonix
 	'''.format(player.first_name,player.target)
 	)

def verify_unique_targets(players):
	targets=[player.target for player in players]
	if len(set(targets))==len(targets):
		return True
	else:
		return False
def email_player_matches(players):
	#Connect to gmail
	print("Connecting to Gmail via SMTP")
	f_credentials=Path(sys.path[0]) / 'private' / 'gmail_credentials.json'
	server=gm.GmailServer()
	server.login(f_credentials)	
	print("Connected and Logged in")

	#Email every player
	for player in players:
		print("Emailing "+player.name)
		email_player_target(player,server)

	#Cleanup
	print("Closing SMTP Connection")
	server.close()

def main():
	print("Secret Santa v"+g_software_version)
	#Import player list and assign matches
	print("Loading Player list")
	player_list_file=Path(sys.path[0]) / 'private' / 'player_list.json'
	players=import_player_list(player_list_file)
	print("Assigning Targets to players")
	engine=MatchEngine(exclusion=True)
	engine.import_players(players)
	engine.match_all_players()
	unique_targets=verify_unique_targets(players)
	if not unique_targets:
		raise ValueError("Player Targets are not unique")
	else:
		print("Verified all targets are unique\n")
	mail_matches=input("Do you want to email players their matches (y/n)?")
	if mail_matches=="y":
		email_player_matches(players)


if __name__=='__main__':
	main()