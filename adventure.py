import pygame,sys, json, math
import os
from pygame.locals import *
pygame.init()
sounds={}
for file in os.listdir("sound/SE"):
	a=file.split(".")
	if a[1]=="wav" or a[1]=="mp3":
		sounds[a[0]]=pygame.mixer.Sound(f"sound/SE/{file}")
	print(sounds)

bgm={}
for file in os.listdir("sound/BGM"):
	a=file.split(".")
	if a[1]=="wav" or a[1]=="mp3":
		bgm[a[0]]=f"sound/BGM/{file}"
	print(bgm)

def bgm_switch(music):
	pygame.mixer.music.stop()
	pygame.mixer.music.unload()
	pygame.mixer.music.load(bgm[music])
	pygame.mixer.music.play(loops=-1)

FPS= 60
fpsClock = pygame.time.Clock()

size=900
resize=size//11
blank=(size%11)/2
state_title="Player State"
mons_title="Monster Battle"
title="Tower of chatgpt"
font=pygame.font.SysFont("arialblack",40)
small_font=pygame.font.SysFont("arialblack",32)
TEXT_COL=(255,255,255)
DISPLAY=pygame.display.set_mode((size,size))
pygame.display.set_caption(title)

bgm_switch("tower")

white=(255,255,255)
black=(0,0,0)

textures={}
for file in os.listdir("texture"):
	s=file.split(".")
	if s[1]=="png":
		textures[s[0]]=pygame.image.load(f'texture/{s[0]}.png')
		textures[s[0]]=pygame.transform.scale(textures[s[0]],(resize,resize))
		print(textures)

data = {
    "lvl":1,
    "hp":2000,
    "atk":10,
    "def":10,
    "money":100,
    "exp":0,
    "keys":{"yellow_key":1,
    "blue_key":1,
    "red_key":1}
}
stage = 0

#讀取地圖資訊
with open("settings/gamemap.json", "r",encoding="utF8") as file:
	mapdata = json.load(file)
Map = mapdata[str(stage)]
pos = Map["point1"]

#讀取怪物資料
with open("settings/monstersetting.json", "r",encoding="utF8") as file:
	monsterdata = json.load(file)
monsimg={}
for x in monsterdata.keys():
	img=pygame.image.load(f'monsters/{monsterdata[x]["name"]}.png')
	oldsize=img.get_size()
	rate=min(resize/oldsize[0],resize/oldsize[1])
	monsimg[x]=pygame.transform.scale(img,(oldsize[0]*rate,oldsize[1]*rate))
print(monsimg)

#讀取道具資料
with open("settings/itemsetting.json", "r",encoding="utF8") as file:
	itemdata = json.load(file)
itemimg={}
for x in itemdata.keys():
	img=pygame.image.load(f'items/{itemdata[x]["name"]}.png')
	oldsize=img.get_size()
	rate=min(resize/oldsize[0],resize/oldsize[1])
	itemimg[x]=pygame.transform.scale(img,(oldsize[0]*rate,oldsize[1]*rate))
print(itemimg)

def open_fence():
	global Map
	global stage
	if stage ==3:
		for j in range(4,7):
			if Map["map"][3][j]!=0:
				return 0
		Map["map"][2][5]=0

def door(x,y,doornum):
	global Map
	global stage
	if doornum==6:
		if data["keys"]["yellow_key"]>=1:
			data["keys"]["yellow_key"]-=1
			Map["map"][x][y]=0
			sounds["door"].play()
	if doornum==7:
		if data["keys"]["blue_key"]>=1:
			data["keys"]["blue_key"]-=1
			Map["map"][x][y]=0
			sounds["door"].play()
	if doornum==8:
		if data["keys"]["red_key"]>=1:
			data["keys"]["red_key"]-=1
			Map["map"][x][y]=0
			sounds["door"].play()

def item(ch,x,y): 
	global Map
	mode=itemdata[ch]["mode"]
	if mode =="key":
		if ch=="I":
			data["keys"]["red_key"]+=1
			data["keys"]["blue_key"]+=1
			data["keys"]["yellow_key"]+=1
		else:
			data["keys"][itemdata[ch]["name"]]+=1
	else:
		data[mode]+=itemdata[ch]["value"]
	Map["map"][x][y]=0
	print(data)
	
def can_defeat(e):
	mst=monsterdata[e]
	plr=data
	dpr=plr["atk"]-mst["def"]
	if dpr >0:
		rd=math.ceil(mst["hp"]/dpr)
		lose=(mst["atk"]-plr["def"])*rd
	else:
		return False
	if plr["atk"]<=mst["def"]:
		return False
	elif lose>=plr["hp"]:
		return False
	else:
		return True

def events(x,y,num):
	global Map
	global stage
	global pos
	if num==4:
		stage+=1
		Map=mapdata[str(stage)]
		pos=Map["point1"]
		sounds["door"].play()
	if num==5:
		stage-=1
		Map=mapdata[str(stage)]
		pos=Map["point2"]
		sounds["door"].play()
	if str(num).isalpha():
		ch=num
		if ord(ch)>=65 and ord(ch)<=90:
			item(ch,x,y)
			sounds["get_item_02"].play()
		elif ord(ch)>=97 and ord(ch)<=122:
			if can_defeat(ch):
				newwindow("monster",ch)
				Map["map"][x][y]=0
				open_fence()
	if num=="=" or num=="[" or num=="_":
		newwindow("shop",num)
	if num=="#":
		newwindow("victory",num)

def draw_text(text,font,text_col,x,y):
	img=font.render(text,True,text_col)
	DISPLAY.blit(img,(x,y))
def shop(e,option):
	if e=="=":
		if data["money"]>=25:
			sounds["menu_select"].play()
			data["money"]-=25
			if option==0:
				data["hp"]+=800
			elif option==1:
				data["atk"]+=4
			elif option==2:
				data["def"]+=4
		else:
			sounds["menu_error"].play()
	elif e=="_":
		if option==0 and data["money"]>=10:
			sounds["menu_select"].play()
			data["money"]-=10
			data["keys"]["yellow_key"]+=1
		elif option==1 and data["money"]>=50:
			sounds["menu_select"].play()
			data["money"]-=50
			data["keys"]["blue_key"]+=1
		elif option==2 and data["money"]>=100:
			sounds["menu_select"].play()
			data["money"]-=100
			data["keys"]["red_key"]+=1
		else:
			sounds["menu_error"].play()
	elif e=="[":
		if option==0 and data["exp"]>=30:
			sounds["menu_select"].play()
			data["exp"]-=30
			data["atk"]+=5
		elif option==1 and data["exp"]>=30:
			sounds["menu_select"].play()
			data["exp"]-=30
			data["def"]+=5
		elif option==2 and data["exp"]>=100:
			sounds["menu_select"].play()
			data["exp"]-=100
			data["lvl"]+=1
			data["atk"]+=13
			data["def"]+=13
			data["hp"]+=1000
		else:
			sounds["menu_error"].play()

def newwindow(Tp,e="None"):
	if Tp=="state":
		new_screen=pygame.display.set_mode((size//1.5,size//1.5))
		pygame.display.set_caption(state_title)
	elif Tp=="monster":
		bgm_switch("battle")
		new_screen=pygame.display.set_mode((size,size//1.5))
		pygame.display.set_caption(mons_title)
		with open("settings/monstersetting.json", "r",encoding="utF8") as file:
			monsterdata = json.load(file)
	elif Tp=="shop":
		new_screen=pygame.display.set_mode((size//2,size//2))
		pygame.display.set_caption("shop")
		option=0
	elif Tp=="victory":
		new_screen=pygame.display.set_mode((size,size))
		pygame.display.set_caption("VICTORY")
		draw_text(f"congratulations! you won",font,TEXT_COL,100,150)
		pygame.display.flip()
		sounds["victory"].play()
		pygame.time.wait(10000)
		pygame.quit()
		sys.exit()
	running=True
	while running:
		if Tp=="state":
			text_array=["LEVEL","HP","ATTACK","DEFENSE","MONEY","EXP"]
			index_arr=["lvl","hp","atk","def","money","exp"]
			for k in range(len(text_array)):
				draw_text(text_array[k],font,TEXT_COL,10,10+k*50)
				draw_text(str(data[index_arr[k]]),font,TEXT_COL,250,10+k*50)
			DISPLAY.blit(itemimg["A"],(10,310))
			DISPLAY.blit(itemimg["B"],(10,380))
			DISPLAY.blit(itemimg["C"],(10,450))
			draw_text(str(data["keys"]["yellow_key"]),font,TEXT_COL,150,310)
			draw_text(str(data["keys"]["blue_key"]),font,TEXT_COL,150,380)
			draw_text(str(data["keys"]["red_key"]),font,TEXT_COL,150,450)
		elif Tp=="monster":
			mst=monsterdata[e]
			plr=data
			px1=200
			px2=size-400
			bg=pygame.Surface(DISPLAY.get_size())
			DISPLAY.blit(bg,(0,0))
			DISPLAY.blit(monsimg[e],(50,310))
			draw_text(f'HP',font,TEXT_COL,px1,130)
			draw_text(f'{mst["hp"]}',font,TEXT_COL,px1,180)
			draw_text(f'ATTACK',font,TEXT_COL,px1,230)
			draw_text(f'{mst["atk"]}',font,TEXT_COL,px1,280)
			draw_text(f'DEFENSE',font,TEXT_COL,px1,330)
			draw_text(f'{mst["def"]}',font,TEXT_COL,px1,380)
			DISPLAY.blit(textures["animal_deer"],(size-150,310))
			draw_text(f'HP',font,TEXT_COL,px2,130)
			draw_text(f'{plr["hp"]}',font,TEXT_COL,px2,180)
			draw_text(f'ATTACK',font,TEXT_COL,px2,230)
			draw_text(f'{plr["atk"]}',font,TEXT_COL,px2,280)
			draw_text(f'DEFENSE',font,TEXT_COL,px2,330)
			draw_text(f'{plr["def"]}',font,TEXT_COL,px2,380)
			

			if mst["hp"]>0:
				damage=(plr["atk"]-mst["def"])
				if damage<=0:
					damage=0
				mst["hp"]-=damage
				sounds["hit"].play()
				pygame.time.wait(200)

				damage=(mst["atk"]-plr["def"])
				if damage<=0:
					damage=0
				plr["hp"]-=damage
				sounds["get_hit"].play()
				pygame.time.wait(200)
			else:
				plr["exp"]+=mst["exp"]
				plr["money"]+=mst["money"]
				pygame.time.wait(500)
				sounds["get_item"].play()
				pygame.display.set_mode((size,size))
				pygame.display.set_caption(title)
				running=False
				bgm_switch("tower")
		elif Tp=="shop":
			bg=pygame.Surface(DISPLAY.get_size())
			DISPLAY.blit(bg,(0,0))
			if e== "=":
				draw_text(f'Welcome! Pay 25$ for:',small_font,TEXT_COL,30,60)
				draw_text(f'800 HP',small_font,TEXT_COL,150,160)
				draw_text(f'4 Attack',small_font,TEXT_COL,150,220)
				draw_text(f'4 defense',small_font,TEXT_COL,150,280)
				draw_text(f'Leave',small_font,TEXT_COL,150,340)
			if e== "[":
				draw_text(f'Welcome! Pay exp for:',small_font,TEXT_COL,30,60)
				draw_text(f'5 Def(30exp)',small_font,TEXT_COL,110,160)
				draw_text(f'5 Atk(30exp)',small_font,TEXT_COL,110,220)
				draw_text(f'1 Lvl(100exp)',small_font,TEXT_COL,100,280)
				draw_text(f'Leave',small_font,TEXT_COL,150,340)
			if e== "_":
				draw_text(f'Welcome! Pay $$ for:',small_font,TEXT_COL,30,60)
				draw_text(f'yellow key(10$)',small_font,TEXT_COL,80,160)
				draw_text(f'blue key(50$)',small_font,TEXT_COL,100,220)
				draw_text(f'red key(100$)',small_font,TEXT_COL,100,280)
				draw_text(f'Leave',small_font,TEXT_COL,150,340)

			if option==0:
				pygame.draw.rect(DISPLAY,(255,255,255),[60,160,300,50],3)
			if option==1:
				pygame.draw.rect(DISPLAY,(255,255,255),[60,220,300,50],3)
			if option==2:
				pygame.draw.rect(DISPLAY,(255,255,255),[60,280,300,50],3)
			if option==3:
				pygame.draw.rect(DISPLAY,(255,255,255),[60,340,300,50],3)
		for event in pygame.event.get():
			if Tp=="state":
				if event.type==pygame.QUIT:
					pygame.quit()
					sys.exit()
				elif event.type==pygame.KEYDOWN :
					if event.key==pygame.K_e:
						pygame.display.set_mode((size,size))
						pygame.display.set_caption(title)
						running=False
			if Tp=="shop":
				if event.type==pygame.QUIT:
					pygame.quit()
					sys.exit()
				elif event.type==pygame.KEYDOWN :
					if event.key==pygame.K_DOWN:
						option=(option+1)%4
						sounds["menu_move"].play()
					if event.key==pygame.K_UP:
						option=(option-1)%4
						sounds["menu_move"].play()
					if event.key==pygame.K_SPACE:
						shop(e,option)
						if option==3:
							pygame.display.set_mode((size,size))
							pygame.display.set_caption(title)
							running=False
						
		pygame.display.flip()
while True:
	DISPLAY.fill(white)
	#貼最底層的地板
	index=0
	indey=0
	for i in Map["map"]:
		for j in i :
			DISPLAY.blit(textures["0"],(blank+index*resize,blank+indey*resize))
			index+=1
		index=0	
		indey+=1

	#貼門,怪物之類的第二層
	index=0
	indey=0
	for i in Map["map"]:
		store_set=0
		for j in i :
			if str(j).isdigit():
				DISPLAY.blit(textures[str(j)],(blank+index*resize,blank+indey*resize))
			elif str(j).isalpha() and ord(j)>=65 and ord(j)<=90:
				DISPLAY.blit(itemimg[j],(blank+index*resize,blank+indey*resize))
			elif str(j).isalpha() and ord(j)>=97 and ord(j)<=122:
				DISPLAY.blit(monsimg[j],(blank+index*resize,blank+indey*resize))
			elif j=="=" and store_set==0:
				DISPLAY.blit(textures["store_side"],(blank+index*resize,blank+indey*resize))
				store_set=1
			elif j=="=" and store_set==1:
				DISPLAY.blit(textures["store_middle"],(blank+index*resize,blank+indey*resize))
				store_set=0
			else:
				DISPLAY.blit(textures[str(j)],(blank+index*resize,blank+indey*resize))	
			index+=1
		index=0	
		indey+=1
	
	DISPLAY.blit(textures["animal_deer"],(blank+pos[1]*resize,blank+pos[0]*resize))
	for event in pygame.event.get():
		if event.type==pygame.QUIT:
			pygame.quit()
			sys.exit()
		if event.type==pygame.KEYDOWN :
			if event.key==K_UP:
				if pos[0]>0 :
					if Map["map"][pos[0]-1][pos[1]]==0:
						sounds["pop"].play()
						pos[0]-=1
					elif str(Map["map"][pos[0]-1][pos[1]]).isdigit() and Map["map"][pos[0]-1][pos[1]]>=6:
						door(pos[0]-1,pos[1],Map["map"][pos[0]-1][pos[1]])
					else:
						events(pos[0]-1,pos[1],Map["map"][pos[0]-1][pos[1]])
			if event.key==K_DOWN :
				if pos[0]<10 :
					if Map["map"][pos[0]+1][pos[1]]==0:
						pos[0]+=1
						sounds["pop"].play()
					elif str(Map["map"][pos[0]+1][pos[1]]).isdigit() and Map["map"][pos[0]+1][pos[1]]>=6:
						door(pos[0]+1,pos[1],Map["map"][pos[0]+1][pos[1]])
					else:
						events(pos[0]+1,pos[1],Map["map"][pos[0]+1][pos[1]])
			if event.key==K_RIGHT:
				if pos[1]<10 :
					if Map["map"][pos[0]][pos[1]+1]==0:
						sounds["pop"].play()
						pos[1]+=1
					elif str(Map["map"][pos[0]][pos[1]+1]).isdigit() and Map["map"][pos[0]][pos[1]+1]>=6:
						door(pos[0],pos[1]+1,Map["map"][pos[0]][pos[1]+1])
					else:
						events(pos[0],pos[1]+1,Map["map"][pos[0]][pos[1]+1])
			if event.key==K_LEFT:
				if pos[1]>0 :
					if Map["map"][pos[0]][pos[1]-1]==0:
						sounds["pop"].play()
						pos[1]-=1
					elif str(Map["map"][pos[0]][pos[1]-1]).isdigit() and Map["map"][pos[0]][pos[1]-1]>=6:
						door(pos[0],pos[1]-1,Map["map"][pos[0]][pos[1]-1])
					else:
						events(pos[0],pos[1]-1,Map["map"][pos[0]][pos[1]-1])
			if event.key==K_e:
				newwindow("state")
	pygame.display.update()
	fpsClock.tick(FPS)
