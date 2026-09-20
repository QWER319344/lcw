import pygame
import random
import sys

pygame.init()
SCREEN_WIDTH = 800; SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("植物大战僵尸【自定义版本】")
clock = pygame.time.Clock(); FPS = 60

WHITE=(255,255,255); RED=(220,30,30); GREEN=(40,180,40); BROWN=(100,70,30); BLACK=(0,0,0)
YELLOW=(255,220,0); GRAY=(150,150,150); ORANGE=(255,140,0)

GRID_W=80; GRID_H=100; ROW_NUM=5; COL_NUM=9; BATTLE_START_Y=100

def load_img(path,w,h):
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img,(w,h))
    except FileNotFoundError:
        s = pygame.Surface((w,h),pygame.SRCALPHA)
        pygame.draw.rect(s,(120,120,120),[0,0,w,h],3)
        return s

bg = load_img("grass_bg.png", SCREEN_WIDTH, SCREEN_HEIGHT)
sunflower_img = load_img("sunflower.png", 60, 60)
peashooter_img = load_img("peashooter.png", 60, 60)
pea_img = load_img("pea.png", 16, 16)
zombie_img = load_img("zombie.png", 60, 80)
wallnut_img = load_img("wallnut.png", 60, 60)
boss_img = load_img("drboss.png", 120, 160)
zombie_kid_img = load_img("zombie_kid.png", 100, 120)

class Sun:
    def __init__(self,x,y): self.x=x; self.y=y; self.value=25; self.life_timer=600
    def update(self): self.life_timer-=1; return self.life_timer<=0
    def draw(self,surf): pygame.draw.circle(surf,YELLOW,(int(self.x+30),int(self.y+30)),22)

class Pea:
    def __init__(self,x,y): self.x=x; self.y=y; self.speed=7; self.damage=25
    def update(self): self.x+=self.speed; return self.x>SCREEN_WIDTH
    def draw(self,surf): surf.blit(pea_img,(self.x,self.y))

class ZombieBullet:
    def __init__(self,x,y): self.x=x; self.y=y; self.speed=4; self.damage=20; self.w=14; self.h=14
    def update(self): self.x-=self.speed; return self.x<-20
    def draw(self,surf):
        pygame.draw.circle(surf,ORANGE,(int(self.x),int(self.y)),7)
        pygame.draw.circle(surf,BLACK,(int(self.x),int(self.y)),7,2)

class SunFlowerPlant:
    def __init__(self,gx,gy):
        self.gx=gx; self.gy=gy
        self.x=gx*GRID_W; self.y=gy*GRID_H+BATTLE_START_Y
        self.cost=50; self.hp=100; self.sun_cd=220
    def update(self,sun_list):
        self.sun_cd-=1
        if self.sun_cd<=0:
            sun_list.append(Sun(random.randint(100,700),random.randint(BATTLE_START_Y+20,520)))
            self.sun_cd=220
    def draw(self,surf): surf.blit(sunflower_img,(self.x,self.y))

class PeaShooterPlant:
    def __init__(self,gx,gy):
        self.gx=gx; self.gy=gy
        self.x=gx*GRID_W; self.y=gy*GRID_H+BATTLE_START_Y
        self.cost=100; self.hp=100; self.shoot_cd=60
    def update(self,bullet_list,enemies):
        self.shoot_cd-=1
        if self.shoot_cd<=0:
            if any(e.gy==self.gy and e.x>self.x for e in enemies):
                bullet_list.append(Pea(self.x+60,self.y+22)); self.shoot_cd=60
    def draw(self,surf): surf.blit(peashooter_img,(self.x,self.y))

class WallNut:
    def __init__(self,gx,gy):
        self.gx=gx; self.gy=gy
        self.x=gx*GRID_W; self.y=gy*GRID_H+BATTLE_START_Y
        self.cost=50; self.hp=600; self.max_hp=600
    def update(self,sun_list): pass
    def draw(self,surf):
        surf.blit(wallnut_img,(self.x,self.y))
        bar_w=60
        pygame.draw.rect(surf,BLACK,(self.x,self.y-8,bar_w,5))
        pygame.draw.rect(surf,GREEN,(self.x,self.y-8,bar_w*(self.hp/self.max_hp),5))

class Zombie:
    def __init__(self,row):
        self.gy=row; self.x=SCREEN_WIDTH; self.y=row*GRID_H+BATTLE_START_Y
        self.hp=80; self.max_hp=80; self.speed=0.55; self.attack_cd=0
    def update(self,plant_list):
        bp=None
        for p in plant_list:
            if p.gy==self.gy and p.x>=self.x-20: bp=p; break
        if bp:
            self.attack_cd-=1
            if self.attack_cd<=0: bp.hp-=8; self.attack_cd=40
        else: self.x-=self.speed
        return self.x<0 or self.hp<=0
    def draw(self,surf):
        surf.blit(zombie_img,(self.x,self.y))
        bar_w=60
        pygame.draw.rect(surf,BLACK,(self.x,self.y-8,bar_w,5))
        pygame.draw.rect(surf,RED,(self.x,self.y-8,bar_w*(self.hp/self.max_hp),5))

class DrBoss:
    def __init__(self,row):
        self.gy=row; self.x=SCREEN_WIDTH-130; self.y=row*GRID_H+BATTLE_START_Y
        self.hp=1000; self.max_hp=1000
    def update(self,plant_list): return self.hp<=0
    def draw(self,surf):
        surf.blit(boss_img,(self.x,self.y))
        bar_w=120
        pygame.draw.rect(surf,BLACK,(self.x,self.y-12,bar_w,8))
        pygame.draw.rect(surf,RED,(self.x,self.y-12,bar_w*(self.hp/self.max_hp),8))

class ZombieKid:
    def __init__(self,row):
        self.gy=row; self.x=SCREEN_WIDTH-100; self.y=row*GRID_H+BATTLE_START_Y-20
        self.hp=250; self.max_hp=250; self.speed=1.2; self.attack_cd=0; self.shoot_cd=120
    def update(self,plant_list,zombie_bullets):
        bp=None
        for p in plant_list:
            if p.gy==self.gy and p.x>=self.x-20: bp=p; break
        if bp:
            self.attack_cd-=1
            if self.attack_cd<=0: bp.hp-=12; self.attack_cd=20
        else: self.x-=self.speed
        self.shoot_cd-=1
        if self.shoot_cd<=0:
            zombie_bullets.append(ZombieBullet(self.x,self.y+50)); self.shoot_cd=120
        return self.x<-100 or self.hp<=0
    def draw(self,surf):
        surf.blit(zombie_kid_img,(self.x,self.y))
        bar_w=100
        pygame.draw.rect(surf,BLACK,(self.x,self.y-10,bar_w,6))
        pygame.draw.rect(surf,ORANGE,(self.x,self.y-10,bar_w*(self.hp/self.max_hp),6))

sun_total=2000
plants=[]; bullets=[]; zombies=[]; boss_list=[]; zombie_kid_list=[]; sun_items=[]; zombie_bullets=[]
total_normal_zombie=100; total_boss=10; total_zombie_kid=3
remain_normal_zombie=total_normal_zombie; remain_boss=total_boss; remain_zombie_kid=total_zombie_kid
spawned_normal_count=0; spawn_timer=0; spawn_interval=45
game_over=False; win=False; selected_plant=None
btn_list=[
    {"name":"sunflower","rect":pygame.Rect(10,10,70,70),"cost":50,"img":sunflower_img},
    {"name":"peashooter","rect":pygame.Rect(90,10,70,70),"cost":100,"img":peashooter_img},
    {"name":"wallnut","rect":pygame.Rect(170,10,70,70),"cost":50,"img":wallnut_img},
]
font=pygame.font.Font(None,24)

while True:
    clock.tick(FPS)
    mx,my=pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type==pygame.QUIT: pygame.quit(); sys.exit()
        if event.type==pygame.MOUSEBUTTONDOWN and not game_over and not win:
            for btn in btn_list:
                if btn["rect"].collidepoint(mx,my): selected_plant=btn["name"]; break
            else:
                for s in sun_items[:]:
                    if pygame.Rect(s.x,s.y,60,60).collidepoint(mx,my):
                        sun_total+=s.value; sun_items.remove(s); break
                if my>=BATTLE_START_Y:
                    gx=mx//GRID_W; gy=(my-BATTLE_START_Y)//GRID_H
                    if 0<=gx<COL_NUM and 0<=gy<ROW_NUM and selected_plant:
                        if not any(p.gx==gx and p.gy==gy for p in plants):
                            if selected_plant=="sunflower" and sun_total>=50:
                                plants.append(SunFlowerPlant(gx,gy)); sun_total-=50
                            elif selected_plant=="peashooter" and sun_total>=100:
                                plants.append(PeaShooterPlant(gx,gy)); sun_total-=100
                            elif selected_plant=="wallnut" and sun_total>=50:
                                plants.append(WallNut(gx,gy)); sun_total-=50

    if not game_over and not win:
        spawn_timer+=1
        if spawn_timer>=spawn_interval:
            spawn_timer=0
            if remain_normal_zombie>0:
                zombies.append(Zombie(random.randint(1,ROW_NUM-1)))
                remain_normal_zombie-=1; spawned_normal_count+=1
                if spawned_normal_count%3==0 and remain_boss>0:
                    boss_list.append(DrBoss(random.randint(1,ROW_NUM-1))); remain_boss-=1
                if spawned_normal_count%30==0 and remain_zombie_kid>0:
                    zombie_kid_list.append(ZombieKid(random.randint(2,3))); remain_zombie_kid-=1

        for p in plants[:]:
            if isinstance(p,SunFlowerPlant): p.update(sun_items)
            elif isinstance(p,PeaShooterPlant): p.update(bullets,zombies+zombie_kid_list)
            elif isinstance(p,WallNut): p.update(sun_items)
            if p.hp<=0: plants.remove(p)

        for z in zombies[:]:
            if z.update(plants):
                if z.x<=0: game_over=True
                zombies.remove(z)
        for boss in boss_list[:]:
            if boss.update(plants): boss_list.remove(boss)
        for k in zombie_kid_list[:]:
            if k.update(plants,zombie_bullets):
                if k.x<=-100: game_over=True
                zombie_kid_list.remove(k)

        db=[]
        for b in bullets:
            out=b.update()
            if out: db.append(b); continue
            hit=False
            for z in zombies[:]:
                if pygame.Rect(z.x,z.y,60,80).colliderect(pygame.Rect(b.x,b.y,16,16)):
                    z.hp-=b.damage; hit=True
                    if z.hp<=0: zombies.remove(z)
                    break
            if not hit:
                for boss in boss_list[:]:
                    if pygame.Rect(boss.x,boss.y,120,160).colliderect(pygame.Rect(b.x,b.y,16,16)):
                        boss.hp-=b.damage; hit=True
                        if boss.hp<=0: boss_list.remove(boss)
                        break
            if not hit:
                for k in zombie_kid_list[:]:
                    if pygame.Rect(k.x,k.y,100,120).colliderect(pygame.Rect(b.x,b.y,16,16)):
                        k.hp-=b.damage; hit=True
                        if k.hp<=0: zombie_kid_list.remove(k)
                        break
            if hit: db.append(b)
        for b in db:
            if b in bullets: bullets.remove(b)

        dz=[]
        for zb in zombie_bullets:
            out=zb.update()
            if out: dz.append(zb); continue
            for p in plants[:]:
                if pygame.Rect(p.x,p.y,60,60).colliderect(pygame.Rect(zb.x-7,zb.y-7,14,14)):
                    p.hp-=zb.damage; dz.append(zb); break
        for zb in dz:
            if zb in zombie_bullets: zombie_bullets.remove(zb)

        for s in sun_items[:]:
            if s.update(): sun_items.remove(s)

        if remain_normal_zombie==0 and remain_boss==0 and remain_zombie_kid==0 \
                and len(zombies)==0 and len(boss_list)==0 and len(zombie_kid_list)==0:
            win=True

    screen.blit(bg,(0,0))
    for r in range(ROW_NUM):
        pygame.draw.line(screen,BROWN,(0,r*GRID_H+BATTLE_START_Y),(SCREEN_WIDTH,r*GRID_H+BATTLE_START_Y),1)
    for c in range(COL_NUM+1):
        pygame.draw.line(screen,BROWN,(c*GRID_W,BATTLE_START_Y),(c*GRID_W,SCREEN_HEIGHT),1)

    for btn in btn_list:
        pygame.draw.rect(screen,GRAY,btn["rect"])
        screen.blit(btn["img"],(btn["rect"].x+5,btn["rect"].y+5))
        if selected_plant==btn["name"]: pygame.draw.rect(screen,YELLOW,btn["rect"],3)

    for s in sun_items: s.draw(screen)
    for p in plants: p.draw(screen)
    for b in bullets: b.draw(screen)
    for zb in zombie_bullets: zb.draw(screen)
    for z in zombies: z.draw(screen)
    for boss in boss_list: boss.draw(screen)
    for k in zombie_kid_list: k.draw(screen)

    screen.blit(font.render(f"阳光：{sun_total}",True,YELLOW),(190,10))
    screen.blit(font.render(f"普通：{remain_normal_zombie}",True,WHITE),(340,10))
    screen.blit(font.render(f"僵王：{remain_boss}",True,RED),(470,10))
    screen.blit(font.render(f"僵王小子：{remain_zombie_kid}",True,ORANGE),(580,10))

    if game_over: screen.blit(font.render("游戏结束！僵尸突破防线！",True,RED),(180,260))
    if win: screen.blit(font.render("🎉 恭喜！全部僵尸消灭，游戏胜利！",True,GREEN),(160,260))

    pygame.display.flip()
