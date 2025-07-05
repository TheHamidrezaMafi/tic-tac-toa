import socket
import pickle
import threading
import random 
import time

host = '127.0.0.1'
port = 8888
backlog = 20
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen(backlog)
#server_socket.settimeout(0.1)

# player_socket_mutex = threading.Semaphore(1)
mutex = threading.Semaphore(1)
player_names= []
games = []

class game_XO:
    def __init__(self,p1 ,p2) -> None:
        self.game_mutex = threading.Lock()
        self.player1 = p1
        self.player2 = p2
        self.game_mode = 0
        self.table = None
        self.turn = None
        self.left_spaces = None
    def get_mode(self):
        self.player1.send_message(["game_mode"])

    def get_turn_name(self):
        a = [self.player1,self.player2]
        return a[self.turn].name
    
    def get_not_turn_name(self):
        a = [self.player1,self.player2]
        return a[(self.turn+1)%2].name
    
    def get_player_by_name(self,m):
        if self.player1.name == m :
            return self.player1
        return self.player2  
    
    # send message of game start to both players and choose a random player to start
    def start_game(self):
        self.table = [[0 for _ in range (self.game_mode )]for __ in range(self.game_mode )]
        self.turn = random.choice([0,1])
        self.send_both(["game_start",self.get_turn_name(),self.table,self.game_mode])

    # sends the message to both players clients
    def send_both(self , m):
        self.player1.send_message(m)
        self.player2.send_message(m)

    # new game moves sent from players getting check to see if they are possible or not
    def submit_move(self,m): 
        if self.get_turn_name() == m[1] :
            if self.table[m[2][0]][m[2][1]] == 0 :
                self.table[m[2][0]][m[2][1]] = self.turn + 1
                self.turn = (self.turn +1 )%2
                self.send_both(["update_game",self.table,self.get_turn_name()])
                self.left_spaces -= 1
                if self.check_ending(m[2]):
                    self.send_both(["game_ended","win",self.get_not_turn_name()])
                    self.player1.status = "available"
                    self.player2.status = "available"
                    self.player1.game = None
                    self.player2.game = None
                    return
                if self.left_spaces == 0 :
                    self.send_both(["game_ended","draw"])
                    self.player1.status = "available"
                    self.player2.status = "available"
                    return
            else :
                self.get_player_by_name(m[1]).send_message(["error","can't place here!"])
        else :
            self.get_player_by_name(m[1]).send_message(["error","not your turn!"])


    # check the game state to see if a player has won      
    def check_ending(self,place):
        x = place[0]
        y = place[1]
        xo = self.table[x][y]
        if self.game_mode == 3 or self.game_mode == 4 :
            for i in range(0 , 3):
                row = True
                for j in range(0,3):
                    if x-i+j >= 0 and x-i+j <self.game_mode:
                        if self.table[x-i+j][y] != xo:
                            row = False
                    else :
                        row = False
                if row :
                    return True
            for i in range(0 , 3):
                row = True
                for j in range(0,3):
                    if y-i+j >= 0 and y-i+j <self.game_mode:
                        if self.table[x][y-i+j] != xo:
                            row = False
                    else :
                        row = False
                if row :
                    return True
            for i in range(0,3):
                row = True
                for j in range(0,3):
                    if y-i+j >= 0 and y-i+j <self.game_mode and x-i+j >= 0 and x-i+j <self.game_mode:
                        if self.table[x-i+j][y-i+j] != xo:
                            row = False
                    else :
                        row = False
                if row :
                    return True
            for i in range(0 , 3):
                row = True
                for j in range(0,3):
                    if y+i-j >= 0 and y+i-j <self.game_mode and x-i+j >= 0 and x-i+j <self.game_mode:
                        if self.table[x-i+j][y+i-j] != xo:
                            row = False
                    else :
                        row = False
                if row :
                    return True
        if self.game_mode == 5:
            for i in range(0 , 4):
                row = True
                for j in range(0,4):
                    if x-i+j >= 0 and x-i+j <self.game_mode:
                        if self.table[x-i+j][y] != xo:
                            row = False
                    else :
                        row = False
                if row :
                    return True
            for i in range(0 , 4):
                row = True
                for j in range(0,4):
                    if y-i+j >= 0 and y-i+j <self.game_mode:
                        if self.table[x][y-i+j] != xo:
                            row = False
                    else :
                        row = False
                if row :
                    return True
            for i in range(0,4):
                row = True
                for j in range(0,4):
                    if y-i+j >= 0 and y-i+j <self.game_mode and x-i+j >= 0 and x-i+j <self.game_mode:
                        if self.table[x-i+j][y-i+j] != xo:
                            row = False
                    else :
                        row = False
                if row :
                    return True
            for i in range(0 , 4):
                row = True
                for j in range(0,4):
                    if y+i-j >= 0 and y+i-j <self.game_mode and x-i+j >= 0 and x-i+j <self.game_mode:
                        if self.table[x-i+j][y+i-j] != xo:
                            row = False
                    else :
                        row = False
                if row :
                    return True
        return False
            
                 

    

class player:
    def  __init__(self,player_socket) -> None:
        self.player_socket = player_socket
        self.player_socket_mutex = threading.Semaphore(1)
        self.status = "available"
        self.name = "blank"
        #self.player_socket.settimeout(0.1)
        players_pool.append(self)
        self.game = None
        self.listening()
    def listening(self): #each players thread listen to client for income querys
        while True:
            try:
                #self.player_socket_mutex.acquire()
                data = self.player_socket.recv(4096)
                #self.player_socket_mutex.release()
                recived_data = pickle.loads(data)
                self.handle_message(recived_data)
            except:
                 pass
            
    def handle_message(self,m):
        if m[0] == "clicked":       #sumbit moves from the players with mutex so 2 players dont submit at the same time
                # with self.game.game_mutex:
                    self.game.submit_move(["move",self.name,[m[1],m[2]]])
        elif m[0] == "players_list":   #send client the players list to find 
              self.send_message(player_names)
              opponent_name =[]
              while True:
                try:
                    #player_socket_mutex.acquire()
                    data = self.player_socket.recv(4096)
                    #player_socket_mutex.release()
                    opponent_name = pickle.loads(data)[0]
                    break
                except:
                    pass
              if opponent_name == "waiting":
                  return
              for p in players_pool :
                  if p.name == opponent_name:
                      if p.status == "available":
                        p.send_message(["invited" , self.name])
                        self.send_message(["invitation","sent"])
                        return
                      else :
                          self.send_message(["invitation","not available"])
              self.send_message(["invitation","failed"])
        elif m[0] == "invitation" :
            if m[1] == "accepted":
                for p in players_pool :
                  if p.name == m[2]:
                      p.send_message(["invitation","accepted"])
                      g = game_XO(p,self)
                      self.game = g
                      p.game = g
                      self.status = "in_game"
                      p.status = "in_game"
                      g.get_mode()
                      break
            else :
                for p in players_pool :
                  if p.name == m[2]:
                      p.send_message(["invitation","rejected"])


        elif m[0] == "game_mode": #ask leader player what kind of game they want to play 
            self.game.game_mode = m[1]
            self.game.left_spaces = m[1]*m[1]
            self.game.start_game() 
        


        elif m[0] == "name": # check to see if players selected name is not used by another client
            mutex.acquire()
            if player_names.count(m[1]) == 0 :
                self.send_message(["accepted"])
                player_names.append(m[1])
                self.name = m[1]
            else :
                self.send_message(["rejected"])
            mutex.release()

    def send_message(self,m): # each player socket has its own mutex to avoid race condition while sending datas
        data = pickle.dumps(m)
        self.player_socket_mutex.acquire()
        self.player_socket.send(data)
        time.sleep(0.1)
        self.player_socket_mutex.release()


players_pool_threads = []
players_pool = []


while True:
    try: # lesson to socket to accept new client and create new thread for each one
        client_socket, address = server_socket.accept() 
        new_player = threading.Thread(target=player,args=[client_socket])
        new_player.start()
        players_pool_threads.append(new_player)
    except:
        pass

