import socket
import pygame
import sys
import pickle
import threading
import time



class tic_tac_toe :
	def __init__(self,s) -> None:
		self.BLACK = (0, 0, 0)
		self.server = s 
		self.WHITE = (255, 255, 255)
		self.size = None
		self.window_width = 800
		self.line_length = 5
		self.rec_size = None
		self.table = None
		self.name= None
		self.turn = None
		self.screen = None
		self.running = True
		
	# return the house clicked by user
	def cell_clicked (self,pos):
		Mouse_x, Mouse_y = pos
		if(Mouse_x < 0 or Mouse_y < 0 or Mouse_x > self.window_width or Mouse_y > self.window_width):
			return[False]
		return[True,int(Mouse_x/self.rec_size),int(Mouse_y/self.rec_size)]

	# start game gui and listening to server for any game updates 
	def GUI_starter(self):
		while self.running:
			try:			#recive any new information coming from server
				data = self.server.recv(4096)
				data_recived = pickle.loads(data)
				self.handle_message(data_recived)
			except:
				pass
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.running = False
					pygame.quit()
					sys.exit()
				if event.type == pygame.MOUSEBUTTONDOWN:
					ret = self.cell_clicked(pygame.mouse.get_pos())
					if(ret[0]):
						self.send_message(["clicked",ret[1],ret[2]])
			self.screen.fill(self.WHITE)
			self.draw_grid()
			self.draw_table()
			self.draw_name()
			self.draw_turn()
			pygame.display.update()

	# wait for server to respond with an answer
	def wait_for_server(self):
		while True:
				try:
					data = self.server.recv(4096)
					data_recived = pickle.loads(data)
					self.handle_message(data_recived)
					break
				except:
					pass

	# draw players name in game window 
	def	draw_name(self):
		font = pygame.font.Font(None, 36)
		text_surface = font.render(self.name, True, self.BLACK)
		self.screen.blit(text_surface, (self.window_width+60,self.window_width/4))
	
	# update the turn text in game window 
	def update_turn(self,t):
		self.turn = t

	# handle new messages from server 
	def handle_message(self,m):
		if m[0] == "update_game":
			self.update_table(m[1])
			self.update_turn(m[2])
		elif m[0] == "game_ended":
			if m[1] == "win":
				print(m[2]," has won!")
			if m[1] == "draw":
				print("game ended in a draw!")
			self.running = False 
			self.find_opponent()


		elif m[0] == "invited":
			response = input(m[1]+" has invited you to play ?(y/n)")
			if response == "y":
				print("waiting for game to start...")
				self.send_message(["invitation","accepted",m[1]])
			else:
				self.send_message(["invitation","rejected",m[1]])
				self.find_opponent()
			self.wait_for_server()
		elif m[0] == "invitation":
			if m[1] == "sent":
				print("invitation sent waiting for them...")
				self.wait_for_server()
			if m[1] == "failed":
				print("player wasnt found try again")
				self.find_opponent()
			if m[1] == "not available":
				print("player is not available")
				self.find_opponent()
			if m[1] == "accepted":
				print("player accepted your invitation")
				self.wait_for_server()
			if m[1] == "rejected":
				print("player rejected your invitation")
				self.find_opponent()
				
		elif m[0] == "game_mode":
			response = input("Select game mode (3,4,5) ")
			self.send_message(["game_mode",int(response)])
			self.wait_for_server()
		elif m[0] == "game_start" :
			self.size = m[3]
			self.table = m[2]
			self.rec_size = self.window_width / self.size
			self.update_turn(m[1])
			pygame.init()
			pygame.display.set_caption("X/O")
			self.screen = pygame.display.set_mode((self.window_width+200,self.window_width))
			clock = pygame.time.Clock()
			clock.tick(10) 
			self.running = True 
			self.GUI_starter()
		elif m[0] == "error":
			print(m[1])
		



	#this function draws the black lines in the game screen 
	def draw_grid(self):  
		for i in range(1,self.size):
			pygame.draw.line(self.screen, self.BLACK, (self.rec_size*i, 0), (self.rec_size*i, self.window_width), self.line_length)
			pygame.draw.line(self.screen, self.BLACK, (0,self.rec_size*i), (self.window_width,self.rec_size*i), self.line_length)

	#draws x on game screen at coordinate x y 
	def draw_x(self,x,y):
		pygame.draw.line(self.screen, self.BLACK, (self.rec_size*x + self.rec_size/6,self.rec_size*y + self.rec_size/6), (self.rec_size*x + 5*self.rec_size/6,self.rec_size*y + 5*self.rec_size/6), self.line_length)
		pygame.draw.line(self.screen, self.BLACK, (self.rec_size*x + self.rec_size/6,self.rec_size*y + 5*self.rec_size/6), (self.rec_size*x + 5*self.rec_size/6,self.rec_size*y + self.rec_size/6), self.line_length)

	#draws o on game screen at coordinate x y 
	def draw_o(self,x,y):
		pygame.draw.circle(self.screen, self.BLACK, (self.rec_size*x +self.rec_size*0.5,self.rec_size*y+self.rec_size*0.5) ,self.rec_size/3 , self.line_length)

	#send message to server 
	def send_message(self,m):
			data = pickle.dumps(m)
			self.server.send(data)
	#ask server for players avalible and choose to wait or invite a player
	def find_opponent(self):
		print("who dou you want to play ? (refresh/wait)")
		print("wait for getting invited by other players")
		self.send_message(["players_list"])
		data_recived = None
		while True:
				try:
					data = self.server.recv(4096)
					data_recived = pickle.loads(data)
					break
				except:
					pass
		print(data_recived)
		opponent_name = input()
		if opponent_name == "refresh":
			self.find_opponent()
			return
		if opponent_name == "wait" or opponent_name == "w":
			print("waiting for someone to invite you !")
			self.send_message(["waiting"])
			self.wait_for_server()
			return
		self.send_message([opponent_name])
		
		self.wait_for_server()
		
	# check with server if a name is avalible for player
	def choose_name(self):
		player_name = input("Enter your name : ")
		self.send_message(["name",player_name])
		while True:
			try:			
				data = self.server.recv(4096)
				data_recived = pickle.loads(data)
				if data_recived[0] == "accepted":
					print("your name is accepted")
					self.name = player_name
					self.find_opponent()
					return
				else:
					print("this username already exist")
					self.choose_name()
					return
			except:
				pass
	
	# draw turn text in game window 
	def	draw_turn(self):
		font = pygame.font.Font(None, 36)
		text_surface = font.render("turn: "+self.turn, True, self.BLACK)
		self.screen.blit(text_surface, (self.window_width+10,self.window_width/2))
	# draw game table in game window 
	def draw_table(self):
		for i in range(0,self.size):
			for j in range(0,self.size):
				if self.table[i][j] == 1 :
					self.draw_x(i,j)
				elif self.table[i][j] == 2 :
					self.draw_o(i,j)
					
	#updating new information recived from server to the game screen 
	def update_table(self,table):
		for i in range(0,self.size):
			for j in range(0,self.size):
				if table[i][j] != self.table[i][j]:
					if table[i][j] == 1 :
						self.draw_x(i,j)
					else:
						self.draw_o(i,j)
					self.table[i][j] = table[i][j]
		




def Main():
	host = '127.0.0.1'
	port = 8888
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	s.connect((host,port))
	s.settimeout(0.1)
	tic = tic_tac_toe(s)
	tic.choose_name()




if __name__ == '__main__':
	Main()
