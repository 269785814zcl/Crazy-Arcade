#!/usr/bin/env python
# -*- coding:utf-8 -*-
import pygame
import numpy as np
import copy
from setting import *
from select_player_number import *
from select_character import *


def if_move (xt,yt,unit):  #检查碰撞,返回1为碰撞，返回0为非碰撞
	k = 0
	for i in range (4):
		x = int ((xt[i]) / 50)
		y = int ((yt[i]) / 50)
		if unit[y][x] == 1 or unit[y][x] == 21:
			k = 1
	return k


#检查人物是否死亡,返回[0，0，0，0]无人死亡，返回[1，0，0，0]一号玩家死亡，其余情况以此类推
def if_dead (play_pool,unit,alive):
	t=0
	for i in play_pool:
		k=0
		for j in range(4):
			x = int ((i.x[j]) / 50)
			y = int ((i.y[j]) / 50)
			if unit[y][x] == -2:
				k=1
		alive[t]=k
		t+=1
	return alive


def Dead(play_number,play_pool,K_dir,key_play,alive):#检查死亡人物，删除死亡人物
	play_number-=int(sum(alive))
	t=0
	for i in alive:
		if i:
			play_pool.pop (t)
			K_dir.pop (t)
			key_play.pop (t)
		else:
			t+=1
	return(play_number,play_pool,K_dir,key_play)


def if_boom(boom,play_pool,grid):#改变炸弹是否可过人属性
	for i in boom:
		if grid.unit[i.y][i.x]==2:
			t=0
			for j in play_pool:
				for k in range (4):
					x = int (j.x[k]/ 50)
					y = int (j.y[k] / 50)
					if x==i.x and y==i.y:
						t=1
			if t==0:
				grid.unit[i.y][i.x]=21
	return grid


class Role (object):  #角色数据模板
	def __init__ (self,x,y,v,ch,boom_vlu,boom_ser,unit,h,l):
		self.x_l = 40  #人物宽
		self.y_h = 40  #人物高
		self.bg_x_l = l * 50  #背景宽
		self.bg_y_h = h * 50  #背景高
		self.x = x
		self.y = y
		self.v = v
		self.ch = ch  #角色图片号
		self.boom_vlu=boom_vlu#炸弹容量
		self.boom_ser=boom_ser
		self.unit = unit
		self.x_left = [0,0,self.x_l,self.x_l]  #左边界
		self.x_right = [self.bg_x_l - self.x_l,self.bg_x_l - self.x_l,self.bg_x_l,self.bg_x_l]  #右边界
		self.y_up = [0,self.y_h,0,self.y_h]  #上边界
		self.y_down = [self.bg_y_h - self.y_h,self.bg_y_h,self.bg_y_h - self.y_h,self.bg_y_h]  #下边界

	def move_left (self):
		if self.x[0] - self.v > 0:
			xt = np.array (self.x)
			self.x = xt - self.v
			print ('left')
		else:
			self.x = self.x_left

	def move_right (self):
		if self.x[0] + self.v < self.bg_x_l - self.x_l:
			xt = np.array (self.x)
			self.x = xt + self.v
			print ('right')
		else:
			self.x = self.x_right

	def move_up (self):
		if self.y[0] - self.v > 0:
			yt = np.array (self.y)
			self.y = yt - self.v
			print ('up')
		else:
			self.y = self.y_up

	def move_down (self):
		if self.y[0] + self.v < self.bg_y_h - self.y_h:
			yt = np.array (self.y)
			self.y = yt + self.v
			print ('down')
		else:
			self.y = self.y_down


class Grid (object):  #棋盘数据模板
	def __init__ (self,unit,screen,p_unit,p_boom,p_boom_boom):
		self.unit = unit
		self.screen = screen
		self.p_unit = p_unit
		self.p_boom = p_boom
		self.p_boom_boom=p_boom_boom

	def display (self):
		t_y = 0
		for y in self.unit:
			t_x = 0
			t_y += 1
			for x in y:
				t_x += 1
				if x == 1:
					self.screen.blit (self.p_unit,((t_x - 1) * 50,(t_y - 1) * 50))  # 显示地形单元
				elif x == 2 or x == 21:#x==21表示不可穿透的炸弹
					self.screen.blit (self.p_boom,((t_x - 1) * 50,(t_y - 1) * 50))  # 显示炸弹单元
				elif x == -2 :
					self.screen.blit (self.p_boom_boom,((t_x - 1) * 50,(t_y - 1) * 50))  # 显示炸弹单元

	def boom_add(self,boom):
		for i in boom:
			self.unit[i.y][i.x]=i.cla

	def boom_cut(self,boom_boom,bbb):
		time=10
		for i in boom_boom:
			bbb.append ([i.y,i.x,time])
			for j in range(i.boom_ser):
				if self.unit[i.y-j-1][i.x] !=1:
					bbb.append([i.y-j-1,i.x,time])
				else:
					break
			for j in range (i.boom_ser):
				if self.unit[i.y+j+1][i.x] !=1:
					bbb.append([i.y+j+1,i.x,time])
				else:
					break
			for j in range (i.boom_ser):
				if self.unit[i.y][i.x-j-1] !=1:
					bbb.append ([i.y,i.x-j-1,time])
				else:
					break
			for j in range (i.boom_ser):
				if self.unit[i.y][i.x+j+1] !=1:
					bbb.append([i.y,i.x+j+1,time])
				else:
					break

		t=0
		for i in bbb:
			if i[2]!=0:
				i[2]-=1
				self.unit[i[0]][i[1]]=-2
				t+=1
			else:
				bp=bbb.pop(t)
				self.unit[bp[0]][bp[1]]=0

		return bbb


def Display (screen,play_pool,list_player_picture):  #打印背景和人物
	screen.blit (background,(0,0))  # 显示背景
	for i in play_pool:
		screen.blit (list_player_picture[i.ch],(i.x[0],i.y[0]))  # 显示人物


def contral (key_play,K_dir,play_number):  #响应键盘
	for event in pygame.event.get ():
		if event.type == pygame.QUIT:  # 如果用户按下屏幕上的关闭按钮，触发QUIT事件，程序退出
			pygame.quit ()
			exit ()
		elif event.type == pygame.KEYDOWN:  # 响应用户的操作
			for j in range (play_number):
				for i in range (5):
					if event.key == K_dir[j][i]:
						key_play[j][i] = 1
		elif event.type == pygame.KEYUP:
			for j in range (play_number):
				for i in range (4):
					if event.key == K_dir[j][i]:
						key_play[j][i] = 0

	return key_play


def Define_K_dir (K_dir,key_play,play_number):  #定义按键
	for i in range (play_number):
		key_play1 = [0,0,0,0,0]#左 右 上 下 炸弹
		key_play.append (key_play1)

	if play_number >= 1:
		K_dir.append ([pygame.K_a,pygame.K_d,pygame.K_w,pygame.K_s,pygame.K_e])
	if play_number >= 2:
		K_dir.append ([pygame.K_LEFT,pygame.K_RIGHT,pygame.K_UP,pygame.K_DOWN,pygame.K_KP0])
	if play_number >= 3:
		K_dir.append ([pygame.K_j,pygame.K_l,pygame.K_i,pygame.K_k,pygame.K_o])
	if play_number >= 4:
		K_dir.append ([pygame.K_KP4,pygame.K_KP6,pygame.K_KP8,pygame.K_KP5,pygame.K_KP9])
	return (K_dir,key_play)


def move (key_play,role,unit):  #人物运动判断
	xt = np.array (role.x)
	yt = np.array (role.y)
	if key_play[0] == 1:  #左
		xtt = xt - role.v  #横坐标预处理
		t = if_move (xtt,yt,unit)  #检查横坐标是否碰撞
		if t == 0:  #如果不碰撞
			role.move_left ()  #进行左移操作
	if key_play[1] == 1:
		xtt = xt + role.v
		t = if_move (xtt,yt,unit)
		if t == 0:
			role.move_right ()
	if key_play[2] == 1:
		ytt = yt - role.v
		t = if_move (xt,ytt,unit)
		if t == 0:
			role.move_up ()
	if key_play[3] == 1:
		ytt = yt + role.v
		t = if_move (xt,ytt,unit)
		if t == 0:
			role.move_down ()

class Boom(object):#炸弹数据模板
	def __init__(self,play_ch,x,y,time,boom_ser,cla):
		self.play_ch=play_ch #玩家号码
		self.x=x
		self.y=y
		self.time=time
		self.boom_ser=boom_ser
		self.cla=cla#炸弹类别  2：普通炸弹

def Check_boom_lie(key_play,play_pool,grid,play_number,boom,boom_boom):#检查炸弹放置
	time=100
	for i in range(play_number):
		if key_play[i][4]==1:
			key_play[i][4] =0
			y=int(sum(play_pool[i].y)/200)
			x=int(sum(play_pool[i].x)/200)
			if play_pool[i].boom_vlu>0 and grid.unit[y][x]!=2:
				play_pool[i].boom_vlu-=1
				boom.append(Boom(i,x,y,time,play_pool[i].boom_ser,2))
	t=0
	for i in boom:
		if i.time!=0:
			i.time-=1
			t += 1
		else:
			bp=boom.pop(t)
			boom_boom.append(bp)
			play_pool[bp.play_ch].boom_vlu+=1

	return (boom,boom_boom)






def main ():
	#定义玩家人物形象字典
	list_player_picture = {1:player1_picture,2:player2_picture,3:player3_picture,4:player4_picture}
	#地形单元矩阵
	unit = [[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
			[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
			[1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,1,0,0,0,1],
			[1,0,0,0,0,0,0,1,0,0,1,0,1,0,0,1,0,0,0,1,0,0,0,1],
			[1,0,0,1,0,1,0,1,0,0,1,0,1,0,0,1,0,0,0,0,0,0,0,1],
			[1,0,0,1,0,1,0,1,0,0,1,0,1,0,0,0,0,1,0,1,0,0,0,1],
			[1,0,0,1,0,1,0,1,0,0,0,0,0,0,0,0,0,1,0,1,1,1,1,1],
			[1,0,1,1,0,1,0,1,0,1,0,1,1,1,0,0,0,1,0,0,0,0,0,1],
			[1,0,1,0,0,1,0,0,0,1,0,0,0,0,0,0,0,1,0,0,1,0,0,1],
			[1,0,1,0,0,0,0,0,0,1,0,0,1,0,0,0,0,0,0,0,1,0,0,1],
			[1,0,1,0,1,1,0,0,0,1,1,1,1,1,0,1,0,0,1,1,1,1,0,1],
			[1,0,0,0,1,1,0,1,0,0,0,0,0,1,0,1,0,0,0,0,1,0,0,1],
			[1,0,0,0,1,1,0,1,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,1],
			[1,0,0,0,1,1,0,1,0,0,1,0,1,1,0,1,0,1,1,1,0,0,0,1],
			[1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,1],
			[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],]
	Temp_unit=copy.deepcopy(unit)
	[h,l] = np.array (unit).shape  #计算地图长和宽

	screen = pygame.display.set_mode ((50 * l,50 * h),0,0)
	pygame.display.set_caption ("移动")  # 设置标题

	player_number = select_player_number (screen) #选择玩家数量
	Temp_number=player_number


	play_pool = main_select_character (screen,player_number,unit,h,l)  #选择人物函数
	Temp_play_pool=copy.deepcopy(play_pool)

	while(True):
		play_pool = []  #玩家池
		K_dir = []  #各个玩家对应的按键池
		key_play = []  #玩家按键池
		boom = []  #炸弹池
		boom_boom = []  #炸弹爆炸池
		bbb = []  #炸弹爆炸效果保留池

		unit=copy.deepcopy(Temp_unit)#初始化矩阵棋盘

		player_number=Temp_number#初始化玩家数量
		print(player_number)

		play_pool=copy.deepcopy(Temp_play_pool)#初始化玩家池
		print(play_pool)

		(K_dir,key_play) = Define_K_dir (K_dir,key_play,player_number)  #定义键盘

		grid = Grid (unit,screen,p_unit,p_boom,p_boom_boom) #初始化棋盘

		pygame.display.update ()#更新画面

		while (True):
			clock = pygame.time.Clock ()
			clock.tick (300)

			alive=np.zeros(player_number)

			Display (screen,play_pool,list_player_picture)  #打印背景及玩家图像
			key_play = contral (key_play,K_dir,player_number)  #键盘响应

			(boom,boom_boom)=Check_boom_lie (key_play,play_pool,grid,player_number,boom,boom_boom)

			grid.boom_add(boom)					#更新unit放置炸弹

			grid = if_boom (boom,play_pool,grid)#更新unit，改变炸弹是否可穿透属性

			bbb=grid.boom_cut(boom_boom,bbb)			#更新unit，炸弹爆炸
			boom_boom = []

			grid.display ()  #打印地形单元,炸弹

			pygame.display.update ()  #更新画面

			for i in range (player_number):
				move (key_play[i],play_pool[i],unit)  #人物运动

			alive=if_dead(play_pool,unit,alive)#死亡判断
			if sum(alive):
				(player_number,play_pool,K_dir,key_play)=Dead (player_number,play_pool,K_dir,key_play,alive)

			if player_number<=1:
				break



if __name__ == '__main__':
	main ()
