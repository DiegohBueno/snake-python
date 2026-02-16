# =========================================================
# 1 IMPORTAÇÕES
# =========================================================
# pygame -> biblioteca principal para jogos
# random -> usado para gerar posições aleatórias da comida
import pygame
import random


# =========================================================
# 2 INICIALIZAÇÃO DO PYGAME
# =========================================================
pygame.init()           # inicializa todos os módulos do pygame
pygame.mixer.init()    # inicializa o sistema de som


# =========================================================
# 3 SONS E MÚSICA
# =========================================================
pygame.mixer.music.load("musica_fundo.ogg")   # música de fundo
pygame.mixer.music.set_volume(0.3)            # volume da música

som_comer = pygame.mixer.Sound("comer.wav")       # som ao comer
som_game_over = pygame.mixer.Sound("game_over.wav")  # som de game over


# =========================================================
# 4 CONSTANTES DO JOGO (REGRAS)
# =========================================================
tamanho = 80            # tamanho da cobra (grid)
passo = 80              # quanto a cobra anda por movimento
margem = 2              # margem para não nascer comida na parede

# comida
tamanho_food = int(tamanho * 0.4)
offset_food = (passo - tamanho_food) // 2

# animação da cobra
velocidade_animacao = 1.4
frame_atual = 0

# animação do ovo
egg_size = int(tamanho * 0.5)
egg_frame = 0
egg_anim_speed = 1.1

# controle de velocidade da cobra
tempo_movimento = 0
intervalo_movimento = 220  # ms (quanto maior, mais lento)


# =========================================================
# 5 DIMENSÕES DA TELA
# =========================================================
largura = 1920
altura = 1080

tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("Snake Game")


# =========================================================
# 6 FONTES
# =========================================================
fonte = pygame.font.SysFont(None, 36)
fonte_game_over = pygame.font.SysFont(None, 82)


# =========================================================
# 7 CARREGAMENTO DE SPRITES
# =========================================================

# ---- SPRITES DA COBRA (3 frames por direção)
snake_frames = {
    "UP": [
        pygame.image.load("sprites/Arbok_Back_1.png").convert_alpha(),
        pygame.image.load("sprites/Arbok_Back_2.png").convert_alpha(),
        pygame.image.load("sprites/Arbok_Back_3.png").convert_alpha(),
    ],
    "DOWN": [
        pygame.image.load("sprites/Arbok_Front_1.png").convert_alpha(),
        pygame.image.load("sprites/Arbok_Front_2.png").convert_alpha(),
        pygame.image.load("sprites/Arbok_Front_3.png").convert_alpha(),
    ],
    "LEFT": [
        pygame.image.load("sprites/Arbok_Left_1.png").convert_alpha(),
        pygame.image.load("sprites/Arbok_Left_2.png").convert_alpha(),
        pygame.image.load("sprites/Arbok_Left_3.png").convert_alpha(),
    ],
    "RIGHT": [
        pygame.image.load("sprites/Arbok_Right_1.png").convert_alpha(),
        pygame.image.load("sprites/Arbok_Right_2.png").convert_alpha(),
        pygame.image.load("sprites/Arbok_Right_3.png").convert_alpha(),
    ]
}

# escala todas as sprites da cobra
for direcao in snake_frames:
    snake_frames[direcao] = [
        pygame.transform.scale(img, (tamanho, tamanho))
        for img in snake_frames[direcao]
    ]

# ---- FUNDO (tile)
tile_bg = pygame.image.load("sprites/Tile.png").convert()
tile_bg = pygame.transform.scale(tile_bg, (passo, passo))

# ---- PAREDE
wall_sprite = pygame.image.load("sprites/Wall.png").convert_alpha()
wall_sprite = pygame.transform.scale(wall_sprite, (passo, passo))

# ---- COMIDA
food_sprite = pygame.image.load("sprites/Food.png").convert_alpha()
food_sprite = pygame.transform.scale(food_sprite, (tamanho_food, tamanho_food))

# ---- OVO (corpo da cobra)
egg_frames = [
    pygame.image.load("sprites/egg_1.png").convert_alpha(),
    pygame.image.load("sprites/egg_2.png").convert_alpha(),
]
egg_frames = [
    pygame.transform.scale(img, (egg_size, egg_size))
    for img in egg_frames
]


# =========================================================
# 8 VARIÁVEIS DO JOGO (ESTADO)
# =========================================================
direcao = "RIGHT"
dx = 0
dy = 0

pontuacao = 0
rodando = True
jogando = False
game_over = False

corpo = []
tamanho_cobra = 1

relogio = pygame.time.Clock()


# =========================================================
# 9 POSIÇÃO INICIAL DA COBRA
# =========================================================
x_inicial = (largura // 2) // passo * passo
y_inicial = (altura // 2) // passo * passo
x = x_inicial
y = y_inicial

colunas = largura // passo
linhas = altura // passo


# =========================================================
# 10 CRIAÇÃO DAS PAREDES
# =========================================================
paredes = []

for c in range(colunas):
    paredes.append((c * passo, 0))
    paredes.append((c * passo, (linhas - 1) * passo))

for l in range(linhas):
    paredes.append((0, l * passo))
    paredes.append(((colunas - 1) * passo, l * passo))


# =========================================================
# 11 FUNÇÃO PARA GERAR COMIDA
# =========================================================
def gerar_comida():
    while True:
        cx = random.randrange(margem, colunas - margem) * passo
        cy = random.randrange(margem, linhas - margem) * passo
        if (cx, cy) not in paredes:
            return cx, cy

comida_x, comida_y = gerar_comida()


# =========================================================
# 12 FUNÇÕES AUXILIARES
# =========================================================
def desenhar_fundo():
    for l in range(linhas):
        for c in range(colunas):
            tela.blit(tile_bg, (c * passo, l * passo))


def reiniciar_jogo():
    global x, y, dx, dy, corpo, tamanho_cobra
    global pontuacao, jogando, game_over, direcao
    global frame_atual, comida_x, comida_y

    x = x_inicial
    y = y_inicial
    dx = 0
    dy = 0
    corpo = []
    tamanho_cobra = 1
    pontuacao = 0
    jogando = False
    game_over = False
    direcao = "RIGHT"
    frame_atual = 0
    comida_x, comida_y = gerar_comida()


# =========================================================
# 13 LOOP PRINCIPAL DO JOGO
# =========================================================
while rodando:

    # ---------------- EVENTOS ----------------
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

        if evento.type == pygame.KEYDOWN:

            # iniciar / reiniciar
            if evento.key == pygame.K_SPACE:
                if game_over or not jogando:
                    reiniciar_jogo()
                    jogando = True
                    pygame.mixer.music.play(-1)

            # movimento
            if not game_over:
                if evento.key == pygame.K_RIGHT and dx != -passo:
                    dx, dy = passo, 0
                    direcao = "RIGHT"
                elif evento.key == pygame.K_LEFT and dx != passo:
                    dx, dy = -passo, 0
                    direcao = "LEFT"
                elif evento.key == pygame.K_UP and dy != passo:
                    dx, dy = 0, -passo
                    direcao = "UP"
                elif evento.key == pygame.K_DOWN and dy != -passo:
                    dx, dy = 0, passo
                    direcao = "DOWN"

    # ---------------- ATUALIZAÇÃO ----------------
    if jogando and not game_over:

        frame_atual = (frame_atual + velocidade_animacao) % 3
        egg_frame = (egg_frame + egg_anim_speed) % 2

        x += dx
        y += dy

        if (x, y) in paredes:
            som_game_over.play()
            pygame.mixer.music.stop()
            game_over = True

        if (x, y) == (comida_x, comida_y):
            som_comer.play()
            tamanho_cobra += 1
            pontuacao += 5
            comida_x, comida_y = gerar_comida()

        corpo.append([x, y])
        if len(corpo) > tamanho_cobra:
            corpo.pop(0)

        for parte in corpo[:-1]:
            if parte == [x, y]:
                game_over = True

    # ---------------- DESENHO ----------------
    desenhar_fundo()

    for parede in paredes:
        tela.blit(wall_sprite, parede)

    tela.blit(food_sprite, (comida_x + offset_food, comida_y + offset_food))

    offset_egg = (passo - egg_size) // 2

    for i, parte in enumerate(corpo):
        if i == len(corpo) - 1:
            tela.blit(snake_frames[direcao][int(frame_atual)], parte)
        else:
            tela.blit(
                egg_frames[int(egg_frame)],
                (parte[0] + offset_egg, parte[1] + offset_egg)
            )

    texto = fonte.render(f"Pontuação: {pontuacao}", True, (255, 255, 255))
    tela.blit(texto, (10, 10))

    if game_over:
        texto_go = fonte_game_over.render("GAME OVER", True, (255, 0, 0))
        tela.blit(texto_go, (largura // 2 - texto_go.get_width() // 2, altura // 2 - 60))

    pygame.display.update()
    relogio.tick(7)


pygame.quit()
