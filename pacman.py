import pygame
from board import boards  
import math

pygame.init()

WIDTH,HEIGHT=600,650
screen=pygame.display.set_mode([WIDTH,HEIGHT])
timer=pygame.time.Clock()
fps=60
font=pygame.font.SysFont("Arial",30)
level=boards
PI=math.pi
flicker=0
player_img=[]
turns_allowed=[False,False,False,False]
player_speed=1
score=0
power=False
power_count=0
game_over=False
game_won=False
moving=False
startup_counter=0
eaten_ghosts=[False,False,False,False]
direction_command=0
lives=3

blinky_img=pygame.transform.scale(pygame.image.load(f'assets/ghost_images/red.png'),(25,25))
pinky_img=pygame.transform.scale(pygame.image.load(f'assets/ghost_images/pink.png'),(25,25))
inky_img=pygame.transform.scale(pygame.image.load(f'assets/ghost_images/blue.png'),(25,25))
clyde_img=pygame.transform.scale(pygame.image.load(f'assets/ghost_images/orange.png'),(25,25))
spooked_img=pygame.transform.scale(pygame.image.load(f'assets/ghost_images/powerup.png'),(25,25))
dead_img=pygame.transform.scale(pygame.image.load(f'assets/ghost_images/dead.png'),(25,25))

blinky_x,blinky_y,blinky_direction=39,50,0 
pinky_x,pinky_y,pinky_direction=300,260,2
inky_x,inky_y,inky_direction=240,260,2 
clyde_x,clyde_y,clyde_direction=330,260,2 

player_x,player_y=440,267

targets=[(player_x,player_y),(player_x,player_y),(player_x,player_y),(player_x,player_y)]

blinky_dead,blinky_box=False,False
inky_dead,inky_box=False,False
clyde_dead,clyde_box=False,False
pinky_dead,pinky_box=False,False
ghost_speed=1

class Ghost:
    def __init__(self,x_cord,y_cord,target,speed,img,direct,dead,box,id):
        self.x_pos=x_cord
        self.y_pos=y_cord
        self.center_x=self.x_pos+12
        self.center_y=self.y_pos+12
        self.target=target
        self.speed=speed
        self.img=img
        self.in_box=box
        self.id=id
        self.dead=dead
        self.direction=direct
        self.turns,self.in_box=self.check_collisions()
        self.rect=self.draw()

    def draw(self):
        if (not power and not self.dead) or (eaten_ghosts[self.id] and power and not self.dead):
            screen.blit(self.img,(self.x_pos,self.y_pos))
        elif power and not self.dead and not eaten_ghosts[self.id]:
            screen.blit(spooked_img,(self.x_pos,self.y_pos))
        else:
            screen.blit(dead_img,(self.x_pos,self.y_pos))

        ghost_rect=pygame.rect.Rect((self.center_x-8,self.center_y-8),(20,20))
        return ghost_rect

    def check_collisions(self):
        # R, L, U, d
        num1 = ((HEIGHT - 50) // 32)
        num2 = (WIDTH // 30)
        num3 = 15
        self.turns = [False, False, False, False]
        
        center_x = int(self.center_x)
        center_y = int(self.center_y)

        if 220 < self.x_pos < 350 and 230 < self.y_pos < 300:
            self.in_box = True
            if abs(self.center_x - 285) < 10:  
                self.turns[2] = True  
        else:
            self.in_box = False

       
        if 0 <= center_x // num2 < 29 and 0 <= center_y // num1 < len(level):
            if level[(center_y - num3) // num1][center_x // num2] == 9:
                self.turns[2] = True
            if level[center_y // num1][(center_x - num3) // num2] < 3:
                self.turns[1] = True
            if level[center_y // num1][(center_x + num3) // num2] < 3:
                self.turns[0] = True
            if level[(center_y + num3) // num1][center_x // num2] < 3:
                self.turns[3] = True
            if level[(center_y - num3) // num1][center_x // num2] < 3:
                self.turns[2] = True

            if self.direction == 2 or self.direction == 3:
                if 12 <= center_x % num2 <= 18:
                    if level[(center_y + num3) // num1][center_x // num2] < 3:
                        self.turns[3] = True
                    if level[(center_y - num3) // num1][center_x // num2] < 3:
                        self.turns[2] = True
                if 12 <= center_y % num1 <= 18:
                    if level[center_y // num1][(center_x - num2) // num2] < 3:
                        self.turns[1] = True
                    if level[center_y // num1][(center_x + num2) // num2] < 3:
                        self.turns[0] = True

            if self.direction == 0 or self.direction == 1:
                if 12 <= center_x % num2 <= 18:
                    if level[(center_y + num3) // num1][center_x // num2] < 3:
                        self.turns[3] = True
                    if level[(center_y - num3) // num1][center_x // num2] < 3:
                        self.turns[2] = True
                if 12 <= center_y % num1 <= 18:
                    if level[center_y // num1][(center_x - num3) // num2] < 3:
                        self.turns[1] = True
                    if level[center_y // num1][(center_x + num3) // num2] < 3:
                        self.turns[0] = True
        else:
            self.turns[0] = True
            self.turns[1] = True

        return self.turns, self.in_box

    def move_clyde(self):
        

        if self.direction==0:
            if self.target[0]>self.x_pos and self.turns[0]:
                self.x_pos+=self.speed
            elif not self.turns[0]:
                if self.target[1]>self.y_pos and self.turns[3]:
                    self.direction=3
                    self.y_pos+=self.speed
                elif self.target[1]<self.y_pos and self.turns[2]:
                    self.direction=2
                    self.y_pos-=self.speed
                elif self.target[0]<self.x_pos and self.turns[1]:
                    self.direction=1
                    self.x_pos-=self.speed
                elif self.turns[3]:
                    self.direction=3
                    self.y_pos+=self.speed
            elif self.turns[0]:
                if self.target[1]>self.y_pos and self.turns[3]:
                    self.direction=3
                    self.y_pos+=self.speed
                if self.target[1]<self.y_pos and self.turns[2]:
                    self.direction=2
                    self.y_pos-=self.speed
                else:
                    self.x_pos+=self.speed       

        elif self.direction==1:
            if self.target[1]>self.y_pos and self.turns[3]:
                self.direction = 3
                self.y_pos+=self.speed
            elif self.target[0]<self.x_pos and self.turns[1]:
                self.direction=1
                self.x_pos -= self.speed
            elif not self.turns[1]:
                if self.target[1]>self.y_pos and self.turns[3]:
                    self.direction=3
                    self.y_pos+=self.speed
                elif self.target[1]<self.y_pos and self.turns[2]:
                    self.direction=2
                    self.y_pos-=self.speed
                elif self.target[0]>self.x_pos and self.turns[0]:
                    self.direction=0
                    self.x_pos+=self.speed
                elif self.turns[3]:
                    self.direction=3
                    self.y_pos+=self.speed
                elif self.turns[2]:
                    self.direction=2
                    self.y_pos-=self.speed
                elif self.turns[0]:
                    self.direction=0
                    self.x_pos+=self.speed
            elif self.turns[1]:
                if self.target[1]>self.y_pos and self.turns[3]:
                    self.direction=3
                    self.y_pos+=self.speed
                if self.target[1]<self.y_pos and self.turns[2]:
                    self.direction=2
                    self.y_pos-=self.speed
                else:
                    self.x_pos-=self.speed
        
        
            if self.target[1]<self.y_pos and self.turns[3]:
                self.direction = 3
            elif self.target[0]<self.x_pos and self.turns[1]:
                self.x_pos -= self.speed
            elif not self.turns[1]:
                if self.target[1]>self.y_pos and self.turns[3]:
                    self.direction=3
                    self.y_pos+=self.speed
                elif self.target[1]<self.y_pos and self.turns[2]:
                    self.direction=2
                    self.y_pos-=self.speed
                elif self.target[0]>self.x_pos and self.turns[0]:
                    self.direction=0
                    self.x_pos+=self.speed
                elif self.turns[3]:
                    self.direction=3
                    self.y_pos+=self.speed
                elif self.turns[0]:
                    self.direction=0
                    self.x_pos+=self.speed
            elif self.turns[1]:
                if self.target[1]>self.y_pos and self.turns[3]:
                    self.direction=3
                    self.y_pos+=self.speed
                if self.target[1]<self.y_pos and self.turns[2]:
                    self.direction=2
                    self.y_pos-=self.speed
                else:
                    self.x_pos-=self.speed
 
        elif self.direction==2:
            if self.target[0] < self.x_pos and self.turns[1]:
                self.direction = 1
                self.x_pos -= self.speed
            elif self.target[1] < self.y_pos and self.turns[2]:
                self.direction = 2
                self.y_pos -= self.speed
            elif not self.turns[2]:
                if self.target[1]>self.y_pos and self.turns[3]:
                    self.direction=3
                    self.y_pos+=self.speed
                elif self.target[1]<self.y_pos and self.turns[2]:
                    self.direction=2
                    self.y_pos-=self.speed
                elif self.target[0]<self.x_pos and self.turns[1]:
                    self.direction=1
                    self.x_pos-=self.speed
                elif self.turns[1]:
                    self.direction=1
                    self.x_pos-=self.speed
                elif self.turns[3]:
                    self.direction=3
                    self.y_pos+=self.speed
                
            elif self.turns[2]:
                if self.target[0]>self.x_pos and self.turns[0]:
                    self.direction=0
                    self.x_pos+=self.speed
                if self.target[0]<self.x_pos and self.turns[1]:
                    self.direction=1
                    self.x_pos-=self.speed
                else:
                    self.y_pos+=self.speed

        elif self.direction == 3:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.y_pos += self.speed
            elif not self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                else:
                    self.y_pos += self.speed

        if self.x_pos== 570:
            self.x_pos = 0
        elif self.x_pos == 0:
            self.x_pos = 570
        return self.x_pos, self.y_pos, self.direction

    def move_blinky(self):
        # r, l, u, d
        if self.direction == 0:
            if self.target[0] > self.x_pos and self.turns[0]:
                self.x_pos += self.speed
            elif not self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[0]:
                self.x_pos += self.speed
        elif self.direction == 1:
            if self.target[0] < self.x_pos and self.turns[1]:
                self.x_pos -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[1]:
                self.x_pos -= self.speed
        elif self.direction == 2:
            if self.target[1] < self.y_pos and self.turns[2]:
                self.direction = 2
                self.y_pos -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[2]:
                self.y_pos -= self.speed
        elif self.direction == 3:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.y_pos += self.speed
            elif not self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[3]:
                self.y_pos += self.speed

        # Portal teleportation
        if self.x_pos== 570:
            self.x_pos = 0
        elif self.x_pos == 0:
            self.x_pos = 570

        return self.x_pos, self.y_pos, self.direction

    def move_inky(self):
        # r, l, u, d
        if self.direction == 0:
            if self.target[0] > self.x_pos and self.turns[0]:
                self.x_pos += self.speed
            elif not self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                if self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                else:
                    self.x_pos += self.speed
        elif self.direction == 1:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.direction = 3
            elif self.target[0] < self.x_pos and self.turns[1]:
                self.x_pos -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                if self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                else:
                    self.x_pos -= self.speed
        elif self.direction == 2:
            if self.target[1] < self.y_pos and self.turns[2]:
                self.direction = 2
                self.y_pos -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[2]:
                self.y_pos -= self.speed
        elif self.direction == 3:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.y_pos += self.speed
            elif not self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[3]:
                self.y_pos += self.speed

        if self.x_pos== 570:
            self.x_pos = 0
        elif self.x_pos == 0:
            self.x_pos = 570

        return self.x_pos, self.y_pos, self.direction

    def move_pinky(self):
        # r, l, u, d
        if self.direction == 0:
            if self.target[0] > self.x_pos and self.turns[0]:
                self.x_pos += self.speed
            elif not self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[0]:
                self.x_pos += self.speed
        elif self.direction == 1:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.direction = 3
            elif self.target[0] < self.x_pos and self.turns[1]:
                self.x_pos -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[1]:
                self.x_pos -= self.speed
        elif self.direction == 2:
            if self.target[0] < self.x_pos and self.turns[1]:
                self.direction = 1
                self.x_pos -= self.speed
            elif self.target[1] < self.y_pos and self.turns[2]:
                self.direction = 2
                self.y_pos -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                else:
                    self.y_pos -= self.speed
        elif self.direction == 3:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.y_pos += self.speed
            elif not self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                else:
                    self.y_pos += self.speed

        if self.x_pos== 570:
            self.x_pos = 0
        elif self.x_pos == 0:
            self.x_pos = 570

        return self.x_pos, self.y_pos, self.direction

    def move_out(self):
        if self.dead:
            box_center_x = 285
            box_center_y = 265

            dx = box_center_x - self.center_x
            dy = box_center_y - self.center_y
            
            length = (dx**2 + dy**2)**0.5
            if length > 0:
                dx = dx/length
                dy = dy/length
            self.x_pos += dx * self.speed
            self.y_pos += dy * self.speed
            
            self.x_pos = max(0, min(self.x_pos, WIDTH - 25))
            self.y_pos = max(0, min(self.y_pos, HEIGHT - 25))
            
            self.center_x = self.x_pos + 12
            self.center_y = self.y_pos + 12
            
            if abs(self.center_x - box_center_x) < 5 and abs(self.center_y - box_center_y) < 5:
                self.in_box = True
                self.x_pos = box_center_x - 12 
                self.y_pos = box_center_y - 12
                self.center_x = box_center_x
                self.center_y = box_center_y
        else:
            if 220 < self.x_pos < 350 and 230 < self.y_pos < 300:
                if abs(self.center_x - 285) > 5:
                    if self.center_x < 285:
                        self.x_pos += self.speed
                        self.direction = 0
                    else:
                        self.x_pos -= self.speed
                        self.direction = 1
                else:
                    self.y_pos -= self.speed
                    self.direction = 2
            else:
                if self.direction == 0:
                    self.x_pos += self.speed
                elif self.direction == 1:
                    self.x_pos -= self.speed
                elif self.direction == 2:
                    self.y_pos -= self.speed
                elif self.direction == 3:
                    self.y_pos += self.speed

        return self.x_pos, self.y_pos, self.direction





for i in range (1,5):
    player_img.append(pygame.transform.scale(pygame.image.load(f'assets/player_images/{i}.png'),(25,25)))



def check_collisions(score,power,power_count,eaten_ghosts):
    num1=(HEIGHT-50)//32
    num2=WIDTH//30
    if 0<player_x<570:
        if level[center_y//num1][center_x//num2]==1:
            level[center_y//num1][center_x//num2]=0
            score+=10
        if level[center_y//num1][center_x//num2]==2:
            level[center_y//num1][center_x//num2]=0
            score+=50
            power=True
            power_count=0
            eaten_ghosts=[False,False,False,False]
    return score,power,power_count,eaten_ghosts        
def draw_points():
    score_text=font.render(f'Score: {score}',True,'white')
    screen.blit(score_text,(10,600))
    if power:
        pygame.draw.circle(screen,'blue',(100,600),10)
    for i in range(lives):
        screen.blit(pygame.transform.scale(player_img[0],(20,20)),(450+i*30,600))
    
    # Add game over and win notifications
    if game_over:
        pygame.draw.rect(screen, 'white', [50, 200, 500, 200], 0, 10)
        pygame.draw.rect(screen, 'dark gray', [70, 220, 460, 160], 0, 10)
        gameover_text = font.render('Game Over! Space bar to restart!', True, 'red')
        screen.blit(gameover_text, (100, 300))
    
    if game_won:
        pygame.draw.rect(screen, 'white', [50, 200, 500, 200], 0, 10)
        pygame.draw.rect(screen, 'dark gray', [70, 220, 460, 160], 0, 10)
        gameover_text = font.render('Victory! Space bar to restart!', True, 'green')
        screen.blit(gameover_text, (100, 300))

def draw_board(level):
    num1 = ((HEIGHT - 50) // 32)
    num2 = (WIDTH // 30)
    for i in range(len(level)):
        for j in range(len(level[i])):
            if level[i][j] == 1:
                pygame.draw.circle(screen, 'white', (j * num2 + (0.5 * num2), i * num1 + (0.5 * num1)), 4)
            if level[i][j] == 2 and not flicker:
                pygame.draw.circle(screen, 'white', (j * num2 + (0.5 * num2), i * num1 + (0.5 * num1)), 10)
            if level[i][j] == 3:
                pygame.draw.line(screen, 'blue', (j * num2 + (0.5 * num2), i * num1),
                                 (j * num2 + (0.5 * num2), i * num1 + num1), 3)
            if level[i][j] == 4:
                pygame.draw.line(screen, 'blue', (j * num2, i * num1 + (0.5 * num1)),
                                 (j * num2 + num2, i * num1 + (0.5 * num1)), 3)
            if level[i][j] == 5:
                pygame.draw.arc(screen, 'blue', [(j * num2 - (num2 * 0.4)) - 2, (i * num1 + (0.5 * num1)), num2, num1],
                                0, PI / 2, 3)
            if level[i][j] == 6:
                pygame.draw.arc(screen, 'blue',
                                [(j * num2 + (num2 * 0.5)), (i * num1 + (0.5 * num1)), num2, num1], PI / 2, PI, 3)
            if level[i][j] == 7:
                pygame.draw.arc(screen, 'blue', [(j * num2 + (num2 * 0.5)), (i * num1 - (0.4 * num1)), num2, num1], PI,
                                3 * PI / 2, 3)
            if level[i][j] == 8:
                pygame.draw.arc(screen, 'blue',
                                [(j * num2 - (num2 * 0.4)) - 2, (i * num1 - (0.4 * num1)), num2, num1], 3 * PI / 2,
                                2 * PI, 3)
            if level[i][j] == 9:
                pygame.draw.line(screen, 'white', (j * num2, i * num1 + (0.5 * num1)),
                                 (j * num2 + num2, i * num1 + (0.5 * num1)), 3)
counter=0
direction=0
def draw_player():
    if direction==0:
        screen.blit(player_img[counter//5],(player_x,player_y))
    elif direction==1:
        screen.blit(pygame.transform.flip(player_img[counter//5],True,False),(player_x,player_y))
    elif direction==2:
        screen.blit(pygame.transform.rotate(player_img[counter//5],90),(player_x,player_y))
    elif direction==3:
        screen.blit(pygame.transform.rotate(player_img[counter//5],270),(player_x,player_y))


def check_position(centerx, centery):
    turns = [False, False, False, False]
    num1 = (HEIGHT - 50) // 32
    num2 = (WIDTH // 30)
    num3 = 8

    if centerx // 30 < 29:
        if direction == 0:
            if level[centery // num1][(centerx - num3) // num2] < 3:
                turns[1] = True
        if direction == 1:
            if level[centery // num1][(centerx + num3) // num2] < 3:
                turns[0] = True
        if direction == 2:
            if level[(centery + num3) // num1][centerx // num2] < 3:
                turns[3] = True
        if direction == 3:
            if level[(centery - num3) // num1][centerx // num2] < 3:
                turns[2] = True

        if direction == 2 or direction == 3:
            if 10 <= centerx % num2 <= 16:
                if level[(centery + num3) // num1][centerx // num2] < 3:
                    turns[3] = True
                if level[(centery - num3) // num1][centerx // num2] < 3:
                    turns[2] = True
            if 10 <= centery % num1 <= 18:
                if level[centery // num1][(centerx - num2) // num2] < 3:
                    turns[1] = True
                if level[centery // num1][(centerx + num2) // num2] < 3:
                    turns[0] = True
        if direction == 0 or direction == 1:
            if 10 <= centerx % num2 <= 16:
                if level[(centery + num1) // num1][centerx // num2] < 3:
                    turns[3] = True
                if level[(centery - num1) // num1][centerx // num2] < 3:
                    turns[2] = True
            if 10 <= centery % num1 <= 18:
                if level[centery // num1][(centerx - num3) // num2] < 3:
                    turns[1] = True
                if level[centery // num1][(centerx + num3) // num2] < 3:
                    turns[0] = True
    else:
        turns[0] = True
        turns[1] = True

    return turns

def move_player(play_x,play_y):
    if direction==0 and turns_allowed[0]:
        play_x+=player_speed
    elif direction==1 and turns_allowed[1]:
        play_x-=player_speed
    if direction==2 and turns_allowed[2]:
        play_y-=player_speed
    elif direction==3 and turns_allowed[3]:
        play_y+=player_speed

    return play_x,play_y

def get_targets(blink_x, blink_y, ink_x, ink_y, pink_x, pink_y, clyd_x, clyd_y):
    if player_x < 450:
        runaway_x = 900
    else:
        runaway_x = 0
    if player_y < 450:
        runaway_y = 900
    else:
        runaway_y = 0
    return_target = (380, 400)
    if power:
        if not blinky.dead and not eaten_ghosts[0]:
            blink_target = (runaway_x, runaway_y)
        elif not blinky.dead and eaten_ghosts[0]:
            if 340 < blink_x < 560 and 340 < blink_y < 500:
                blink_target = (400, 100)
            else:
                blink_target = (player_x, player_y)
        else:
            blink_target = return_target
        if not inky.dead and not eaten_ghosts[1]:
            ink_target = (runaway_x, player_y)
        elif not inky.dead and eaten_ghosts[1]:
            if 340 < ink_x < 560 and 340 < ink_y < 500:
                ink_target = (400, 100)
            else:
                ink_target = (player_x, player_y)
        else:
            ink_target = return_target
        if not pinky.dead:
            pink_target = (player_x, runaway_y)
        elif not pinky.dead and eaten_ghosts[2]:
            if 340 < pink_x < 560 and 340 < pink_y < 500:
                pink_target = (400, 100)
            else:
                pink_target = (player_x, player_y)
        else:
            pink_target = return_target
        if not clyde.dead and not eaten_ghosts[3]:
            clyd_target = (450, 450)
        elif not clyde.dead and eaten_ghosts[3]:
            if 340 < clyd_x < 560 and 340 < clyd_y < 500:
                clyd_target = (400, 100)
            else:
                clyd_target = (player_x, player_y)
        else:
            clyd_target = return_target
    else:
        if not blinky.dead:
            if 340 < blink_x < 560 and 340 < blink_y < 500:
                blink_target = (400, 100)
            else:
                blink_target = (player_x, player_y)
        else:
            blink_target = return_target
        if not inky.dead:
            if 340 < ink_x < 560 and 340 < ink_y < 500:
                ink_target = (400, 100)
            else:
                ink_target = (player_x, player_y)
        else:
            ink_target = return_target
        if not pinky.dead:
            if 340 < pink_x < 560 and 340 < pink_y < 500:
                pink_target = (400, 100)
            else:
                pink_target = (player_x, player_y)
        else:
            pink_target = return_target
        if not clyde.dead:
            if 340 < clyd_x < 560 and 340 < clyd_y < 500:
                clyd_target = (400, 100)
            else:
                clyd_target = (player_x, player_y)
        else:
            clyd_target = return_target
    return [blink_target, ink_target, pink_target, clyd_target]

run=True

while run:
    timer.tick(fps)
    if counter < 19:
        counter+=1
        if counter>6:
            flicker=False
    else:
        counter=0
        flicker=True
    if power and power_count<600:
        power_count+=1
    elif power and power_count>=600:
        power_count=0
        power=False
        eaten_ghosts=[False,False,False,False]

    if startup_counter<180:
        moving =False
        startup_counter+=1
    else:
        moving=True

    screen.fill('black')
    center_x = player_x + 12
    center_y = player_y + 12
    draw_board(level)
    player_circle=pygame.draw.circle(screen,'black',(center_x,center_y),12,2)
    draw_player()
    
    game_won = True
    for i in range(len(level)):
        if 1 in level[i] or 2 in level[i]:
            game_won = False
            break

    blinky=Ghost(blinky_x,blinky_y,targets[0],ghost_speed,blinky_img,blinky_direction,blinky_dead,blinky_box,0)
    inky=Ghost(inky_x,inky_y,targets[1],ghost_speed,inky_img,inky_direction,inky_dead,inky_box,1)
    pinky=Ghost(pinky_x,pinky_y,targets[2],ghost_speed,pinky_img,pinky_direction,pinky_dead,pinky_box,2)
    clyde=Ghost(clyde_x,clyde_y,targets[3],ghost_speed,clyde_img,clyde_direction,clyde_dead,clyde_box,3)

    draw_points()
    targets=get_targets(blinky_x,blinky_y,inky_x,inky_y,pinky_x,pinky_y,clyde_x,clyde_y)
    
   

    turns_allowed = check_position(center_x, center_y)
    #print(f"Turns allowed: {turns_allowed}, Direction: {direction}")
    #print(f"position :{player_x} ,{player_y}")
    if player_x==570 and player_y==267:
        player_x=0
    elif player_x==0 and player_y==267:
        player_x=568
    if moving:
        player_x, player_y = move_player(player_x, player_y)
        if not blinky_dead and not blinky.in_box:
            blinky_x,blinky_y,blinky_direction=blinky.move_blinky()
        else:
            blinky_x,blinky_y,blinky_direction=blinky.move_out()
        if not pinky_dead and not pinky.in_box:
            pinky_x, pinky_y, pinky_direction = pinky.move_pinky()
        else:
            pinky_x, pinky_y, pinky_direction = pinky.move_out()
        if not inky_dead and not inky.in_box:
            inky_x, inky_y, inky_direction = inky.move_inky()
        else:
            inky_x, inky_y, inky_direction = inky.move_out()
        if not clyde_dead and not clyde.in_box:
            clyde_x, clyde_y, clyde_direction = clyde.move_clyde()
        else:
            clyde_x, clyde_y, clyde_direction = clyde.move_out()
    score,power,power_count,eaten_ghosts=check_collisions(score,power,power_count,eaten_ghosts)


    if not power:
        if(player_circle.colliderect(blinky.rect) and not blinky.dead) or \
            (player_circle.colliderect(inky.rect) and not inky.dead) or \
            (player_circle.colliderect(pinky.rect) and not pinky.dead) or \
            (player_circle.colliderect(clyde.rect) and not clyde.dead) :
                if lives >0:
                    lives-=1
                    startup_counter=0
                    power=0
                    power_count=0
                    blinky_x,blinky_y,blinky_direction=39,50,0 
                    pinky_x,pinky_y,pinky_direction=300,260,2
                    inky_x,inky_y,inky_direction=240,260,2 
                    clyde_x,clyde_y,clyde_direction=330,280,2 
                    eaten_ghosts=[False,False,False,False]
                    player_x,player_y=440,267
                    direction=0
                    blinky_dead=False
                    inky_dead=False
                    pinky_dead=False
                    clyde_dead=False
                else:
                    game_over=True
                    moving=False

    if power and player_circle.colliderect(blinky.rect) and eaten_ghosts[0] and not blinky.dead:
        if lives > 0:
            power = False
            power_count = 0
            lives -= 1
            startup_counter = 0
            blinky_x,blinky_y,blinky_direction=39,50,0 
            pinky_x,pinky_y,pinky_direction=300,260,2
            inky_x,inky_y,inky_direction=240,260,2 
            clyde_x,clyde_y,clyde_direction=330,280,2 
            eaten_ghosts=[False,False,False,False]
            player_x,player_y=440,267
            direction_command=0
            direction=0
            blinky_dead = False
            inky_dead = False
            clyde_dead = False
            pinky_dead = False
        else:
            game_over = True
            moving = False
            startup_counter = 0
    if power and player_circle.colliderect(inky.rect) and eaten_ghosts[1] and not inky.dead:
        if lives > 0:
            power = False
            power_count = 0
            lives -= 1
            startup_counter = 0
            blinky_x,blinky_y,blinky_direction=39,50,0 
            pinky_x,pinky_y,pinky_direction=300,260,2
            inky_x,inky_y,inky_direction=240,260,2 
            clyde_x,clyde_y,clyde_direction=330,280,2 
            eaten_ghosts=[False,False,False,False]
            player_x,player_y=440,267
            direction_command=0
            direction=0
            blinky_dead = False
            inky_dead = False
            clyde_dead = False
            pinky_dead = False
        else:
            game_over = True
            moving = False
            startup_counter = 0
    if power and player_circle.colliderect(pinky.rect) and eaten_ghosts[2] and not pinky.dead:
        if lives > 0:
            power = False
            power_count = 0
            lives -= 1
            startup_counter = 0
            blinky_x,blinky_y,blinky_direction=39,50,0 
            pinky_x,pinky_y,pinky_direction=300,260,2
            inky_x,inky_y,inky_direction=240,260,2 
            clyde_x,clyde_y,clyde_direction=330,280,2 
            eaten_ghosts=[False,False,False,False]
            player_x,player_y=440,267
            direction=0
            direction_command=0
            blinky_dead = False
            inky_dead = False
            clyde_dead = False
            pinky_dead = False
        else:
            game_over = True
            moving = False
            startup_counter = 0
    if power and player_circle.colliderect(clyde.rect) and eaten_ghosts[3] and not clyde.dead:
        if lives > 0:
            power = False
            power_count = 0
            lives -= 1
            startup_counter = 0
            blinky_x,blinky_y,blinky_direction=39,50,0 
            pinky_x,pinky_y,pinky_direction=300,260,2
            inky_x,inky_y,inky_direction=240,260,2 
            clyde_x,clyde_y,clyde_direction=330,280,2 
            eaten_ghosts=[False,False,False,False]
            player_x,player_y=440,267
            direction=0
            direction_command=0
            blinky_dead = False
            inky_dead = False
            clyde_dead = False
            pinky_dead = False
        else:
            game_over = True
            moving = False
            startup_counter = 0   

    # Ghost death conditions during powerup
    if power and player_circle.colliderect(blinky.rect) and not blinky.dead and not eaten_ghosts[0]:
        blinky_dead = True
        eaten_ghosts[0] = True
        ghost_speed = 2  # Double speed when eaten
    if power and player_circle.colliderect(inky.rect) and not inky.dead and not eaten_ghosts[1]:
        inky_dead = True
        eaten_ghosts[1] = True
        ghost_speed = 2
    if power and player_circle.colliderect(pinky.rect) and not pinky.dead and not eaten_ghosts[2]:
        pinky_dead = True
        eaten_ghosts[2] = True
        ghost_speed = 2
    if power and player_circle.colliderect(clyde.rect) and not clyde.dead and not eaten_ghosts[3]:
        clyde_dead = True
        eaten_ghosts[3] = True
        ghost_speed = 2

    # Ghost revival logic
    if blinky.in_box and blinky_dead:
        blinky_dead = False
        ghost_speed = 1  # Reset speed when revived
    if inky.in_box and inky_dead:
        inky_dead = False
        ghost_speed = 1
    if pinky.in_box and pinky_dead:
        pinky_dead = False
        ghost_speed = 1
    if clyde.in_box and clyde_dead:
        clyde_dead = False
        ghost_speed = 1

    if blinky_dead:
        targets[0] = (285, 265)  
    if inky_dead:
        targets[1] = (285, 265)
    if pinky_dead:
        targets[2] = (285, 265)
    if clyde_dead:
        targets[3] = (285, 265)

    # Replace the AI control section with keyboard controls
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            run=False
        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_RIGHT:
                direction_command=0
            if event.key==pygame.K_LEFT:
                direction_command=1
            if event.key==pygame.K_UP:
                direction_command=2
            if event.key==pygame.K_DOWN:
                direction_command=3
            if event.key==pygame.K_SPACE and (game_over or game_won):
                power=False
                power_count=0
                lives=3
                startup_counter=0
                player_x=440
                player_y=267
                direction=0
                direction_command=0
                blinky_x,blinky_y,blinky_direction=39,50,0 
                pinky_x,pinky_y,pinky_direction=300,260,2
                inky_x,inky_y,inky_direction=240,260,2 
                clyde_x,clyde_y,clyde_direction=330,280,2 
                eaten_ghosts=[False,False,False,False]
                blinky_dead=False
                inky_dead=False
                pinky_dead=False
                clyde_dead=False
                score=0
                level=boards
                game_over=False
                game_won=False

    if direction_command == 0 and turns_allowed[0]:
        direction = 0
    if direction_command == 1 and turns_allowed[1]:
        direction = 1
    if direction_command == 2 and turns_allowed[2]:
        direction = 2
    if direction_command == 3 and turns_allowed[3]:
        direction = 3
            
    if player_x==570:
            player_x=0
    elif player_x==0:
            player_x=570

    pygame.display.flip()

pygame.quit()
