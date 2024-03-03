import pygame
import sys
import random
from typing import Literal


State = Literal['game', 'menu', 'result']
Qst = Literal[0, 1, 2, 3]


# 位置
SIZE = 600, 800


class UserEvent:
    order = pygame.USEREVENT

    def __new__(cls):
        cls.order += 1
        return cls.order


# 游戏切换事件
GAMESHIFT = UserEvent()
QSTSET = UserEvent()
# 游戏内部事件
BLOCK_DOWN =  UserEvent()
NEED_NEXT =  UserEvent()
ELIMINATE_ROWS =  UserEvent()


# 按钮
class Button:
    font: pygame.font.Font

    def __init__(self, text: str, center: tuple[int, int], event: pygame.event.Event) -> None:
        self.img = self.font.render(text, True, "#000000", "#DDDDDD")
        self.rect = self.img.get_rect(center=center)
        self.event = event

        self.border_rect = self.rect.inflate(50, 20)


    def click(self, pos: tuple[int, int]):
        if self.rect.collidepoint(pos):
            pygame.event.post(self.event)


    def draw(self):
        surf = pygame.display.get_surface()
        pygame.draw.rect(surf, "#DDDDDD", self.border_rect)
        surf.blit(self.img, self.rect)


class Result:
    def __init__(self) -> None:
        # 每一张问卷的
        self.qst_list = [
            pygame.image.load(f"res/QTS/{i}.jpg") for i in range(1, 4)
        ]
        self.rect_list = [
            img.get_rect(center=(SIZE[0] / 2, SIZE[1] / 2))
            for img in self.qst_list
        ]
        # 按钮
        self.back_button = Button(
            "点我返回",
            (SIZE[0] / 2, SIZE[1] / 2),
            pygame.event.Event(GAMESHIFT, {"state": "menu", "qst": 0})
        )

    
    def update(self, qst: Qst):
        # 控制
        for event in pygame.event.get(pygame.MOUSEBUTTONDOWN):
            self.back_button.click(event.pos)
        # 绘制
        surf = pygame.display.get_surface()
        surf.blit(self.qst_list[qst - 1], self.rect_list[qst - 1])
        self.back_button.draw()
        

class Menu:
    def __init__(self) -> None:
        self.buttons = [
            Button(
                "测试", (SIZE[0] / 2, SIZE[1] * 3 / 12),
                pygame.event.Event(GAMESHIFT, {"state": "game", "qst": 0})
            ),
            Button(
                "游戏1", (SIZE[0] / 2, SIZE[1] * 5 / 12),
                pygame.event.Event(GAMESHIFT, {"state": "game", "qst": 1})
            ),
            Button(
                "游戏2", (SIZE[0] / 2, SIZE[1] * 7 / 12),
                pygame.event.Event(GAMESHIFT, {"state": "game", "qst": 2})
            ),
            Button(
                "游戏3", (SIZE[0] / 2, SIZE[1] * 9 / 12),
                pygame.event.Event(GAMESHIFT, {"state": "game", "qst": 3})
            )
        ]


    def update(self):
        # 事件处理
        for event in pygame.event.get(pygame.MOUSEBUTTONDOWN):
            for button in self.buttons:
                button.click(event.pos)
        # 绘制
        for button in self.buttons:
            button.draw()


class Block:
    ...


class BlockSys:
    def __init__(self) -> None:
        self.map: dict[tuple[int, int], Block] = {}
    
    def update(self, qst: Qst):
        ...


# 基础game组件
class Windows:
    def __init__(self) -> None:
        pygame.init()
        pygame.font.init()
        self.surface = pygame.display.set_mode(SIZE)
        pygame.display.set_caption("卡牌匹配")
        self.clock = pygame.time.Clock()
        self.quit = False

        Button.font = pygame.font.Font(r'res\font\SmileySans-Oblique-3.otf', 40)


    def update(self):
        ...


    def run(self):
        while not self.quit:
            if pygame.event.get(pygame.QUIT):
                self.quit = True
            self.update()
            pygame.event.clear()
            pygame.display.flip()
            self.clock.tick(60)
        self.safe_quit()


    def safe_quit(self):
        pygame.quit()
        sys.exit()


# 游戏
class Game(Windows):
    def __init__(self) -> None:
        super().__init__()
        # 程序模式
        self.state: State = 'menu'
        self.qst: Qst = 0
        # 3个功能
        self.result = Result()
        self.block_sys = BlockSys()
        self.menu = Menu()


    def set_mode(self):
        if events := pygame.event.get(GAMESHIFT):
            self.state = events[-1].state
        if events := pygame.event.get(QSTSET):
            self.qst = events[-1].qst


    def update(self):        
        self.surface.fill("#334d5c")
        self.set_mode()
        if self.state == 'game':
            self.block_sys.update(self.qst)
        elif self.state == 'menu':
            self.menu.update()
        else:
            self.result.update(self.qst)
    
        return super().update()



Game().run()