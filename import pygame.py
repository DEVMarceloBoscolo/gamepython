import pygame
import random
import sys
import os

# Inicializa o pygame
pygame.init()
pygame.mixer.init()

# Configurações da tela
LARGURA = 400
ALTURA = 600
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Ballrun Deluxe")

# Cores
BRANCO = (255, 255, 255)
VERDE = (0, 255, 0)
AZUL = (0, 0, 255)
AMARELO = (255, 255, 0)
PRETO = (0, 0, 0)
VERMELHO = (255, 0, 0)
ROSA = (255, 105, 180)

# Configurações do jogo
GRAVIDADE = 0.25
PULO = -5
VELOCIDADE_CANOS = 2
ESPACO_CANOS = 150
FREQUENCIA_CANOS = 1500  # ms
DIFICULDADE_INCREMENTO = 0.1

# Fonte
FONTE_PEQUENA = pygame.font.SysFont('Arial', 20)
FONTE_MEDIA = pygame.font.SysFont('Arial', 30)
FONTE_GRANDE = pygame.font.SysFont('Arial', 50)

# Efeitos sonoros (simulados - na prática você precisaria ter arquivos de som)
class Sons:
    def __init__(self):
        # Em um projeto real, carregue arquivos de som aqui
        # pygame.mixer.Sound('pulo.wav')
        self.pulo = None
        self.ponto = None
        self.colisao = None
        self.musica = None

sons = Sons()

class Passaro:
    def __init__(self):
        self.x = 100
        self.y = ALTURA // 2
        self.velocidade = 0
        self.raio = 15
        self.cor = AMARELO
        self.animacao = 0
        self.imagens = []  # Em um jogo real, carregue sprites de animação aqui
        
    def pular(self):
        self.velocidade = PULO
        # if sons.pulo: sons.pulo.play()
        
    def mover(self):
        self.velocidade += GRAVIDADE
        self.y += self.velocidade
        self.animacao = (self.animacao + 1) % 10  # Para animação
        
        # Limites da tela
        if self.y < 0:
            self.y = 0
            self.velocidade = 0
        if self.y > ALTURA:
            self.y = ALTURA
            self.velocidade = 0
            
    def desenhar(self):
        # Animação simples - em um jogo real, use sprites
        tamanho = self.raio + (2 if self.animacao < 5 else 0)
        pygame.draw.circle(TELA, self.cor, (self.x, int(self.y)), tamanho)
        # Desenho do olho
        pygame.draw.circle(TELA, PRETO, (self.x + 5, int(self.y) - 3), 3)
        
    def get_mask(self):
        return pygame.Rect(self.x - self.raio, self.y - self.raio, self.raio * 2, self.raio * 2)

class Cano:
    def __init__(self):
        self.x = LARGURA
        self.altura = random.randint(100, ALTURA - 100 - ESPACO_CANOS)
        self.bottom = self.altura + ESPACO_CANOS
        self.largura = 70
        self.passou = False
        self.cor = VERDE
        self.topo_rect = pygame.Rect(self.x, 0, self.largura, self.altura)
        self.base_rect = pygame.Rect(self.x, self.bottom, self.largura, ALTURA - self.bottom)
        
    def mover(self):
        self.x -= VELOCIDADE_CANOS
        self.topo_rect.x = self.x
        self.base_rect.x = self.x
        
    def desenhar(self):
        # Cano superior
        pygame.draw.rect(TELA, self.cor, self.topo_rect)
        # Borda do cano superior
        pygame.draw.rect(TELA, PRETO, self.topo_rect, 2)
     
        
        # Cano inferior
        pygame.draw.rect(TELA, self.cor, self.base_rect)
        # Borda do cano inferior
        pygame.draw.rect(TELA, PRETO, self.base_rect, 2)
        
        
    def colisao(self, passaro):
        passaro_mask = passaro.get_mask()
        return passaro_mask.colliderect(self.topo_rect) or passaro_mask.colliderect(self.base_rect)

class Fundo:
    def __init__(self):
        self.cor_ceu = (135, 206, 235)  # Azul céu
        self.chao_altura = 50
        self.chao_cor = (139, 69, 19)  # Marrom
        self.nuvens = []
        for _ in range(5):
            self.nuvens.append([random.randint(0, LARGURA), random.randint(0, ALTURA//2), 
                              random.randint(30, 70), random.randint(20, 40)])
        
    def mover_nuvens(self):
        for nuvem in self.nuvens:
            nuvem[0] -= 0.5
            if nuvem[0] < -nuvem[2]:
                nuvem[0] = LARGURA
                nuvem[1] = random.randint(0, ALTURA//2)
                
    def desenhar(self):
        # Céu
        TELA.fill(self.cor_ceu)
        
        # Nuvens
        for nuvem in self.nuvens:
            pygame.draw.ellipse(TELA, BRANCO, (nuvem[0], nuvem[1], nuvem[2], nuvem[3]))
            pygame.draw.ellipse(TELA, BRANCO, (nuvem[0] + 20, nuvem[1] - 10, nuvem[2] - 10, nuvem[3] + 10))
        
        # Chão
        pygame.draw.rect(TELA, self.chao_cor, (0, ALTURA - self.chao_altura, LARGURA, self.chao_altura))
        # Grama no chão
        pygame.draw.rect(TELA, VERDE, (0, ALTURA - self.chao_altura - 5, LARGURA, 5))

class Jogo:
    def __init__(self):
        self.passaro = Passaro()
        self.canos = [Cano()]
        self.pontos = 0
        self.melhor_pontuacao = 0
        self.ultimo_cano = pygame.time.get_ticks()
        self.velocidade_jogo = VELOCIDADE_CANOS
        self.fundo = Fundo()
        self.estado = "menu"  # menu, jogando, gameover
        self.dificuldade = 1.0
        
    def reset(self):
        self.passaro = Passaro()
        self.canos = [Cano()]
        self.pontos = 0
        self.ultimo_cano = pygame.time.get_ticks()
        self.velocidade_jogo = VELOCIDADE_CANOS
        self.dificuldade = 1.0
        
    def atualizar(self):
        self.passaro.mover()
        self.fundo.mover_nuvens()
        
        # Geração de canos
        tempo_atual = pygame.time.get_ticks()
        if tempo_atual - self.ultimo_cano > FREQUENCIA_CANOS / self.dificuldade:
            self.canos.append(Cano())
            self.ultimo_cano = tempo_atual
            # Aumenta a dificuldade gradualmente
            self.dificuldade += 0.01
            self.velocidade_jogo += 0.01
        
        for cano in self.canos[:]:
            cano.mover()
            
            if cano.x + cano.largura < self.passaro.x and not cano.passou:
                cano.passou = True
                self.pontos += 1
                # if sons.ponto: sons.ponto.play()
                if self.pontos > self.melhor_pontuacao:
                    self.melhor_pontuacao = self.pontos
                
            if cano.x < -cano.largura:
                self.canos.remove(cano)
        
        # Verificar colisões
        for cano in self.canos:
            if cano.colisao(self.passaro) or self.passaro.y >= ALTURA - self.fundo.chao_altura or self.passaro.y <= 0:
                # if sons.colisao: sons.colisao.play()
                self.estado = "gameover"
        
    def desenhar(self):
        self.fundo.desenhar()
        
        for cano in self.canos:
            cano.desenhar()
        self.passaro.desenhar()
        
        # Pontuação
        texto_pontos = FONTE_MEDIA.render(f"{self.pontos}", True, BRANCO)
        TELA.blit(texto_pontos, (LARGURA // 2 - texto_pontos.get_width() // 2, 50))
        
        if self.estado == "menu":
            self.desenhar_menu()
        elif self.estado == "gameover":
            self.desenhar_gameover()
    
    def desenhar_menu(self):
        # Sobreposição semi-transparente
        s = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        s.fill((0, 0, 0, 128))
        TELA.blit(s, (0, 0))
        
        # Título
        titulo = FONTE_GRANDE.render("Ballrun", True, AMARELO)
        TELA.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 150))
        
        # Instruções
        instrucao1 = FONTE_MEDIA.render("Pressione ESPAÇO para jogar", True, BRANCO)
        TELA.blit(instrucao1, (LARGURA // 2 - instrucao1.get_width() // 2, 300))
        
        instrucao2 = FONTE_PEQUENA.render("Use ESPAÇO para fazer o pássaro voar", True, BRANCO)
        TELA.blit(instrucao2, (LARGURA // 2 - instrucao2.get_width() // 2, 350))
        
        # Melhor pontuação
        if self.melhor_pontuacao > 0:
            melhor = FONTE_MEDIA.render(f"Melhor: {self.melhor_pontuacao}", True, BRANCO)
            TELA.blit(melhor, (LARGURA // 2 - melhor.get_width() // 2, 400))
    
    def desenhar_gameover(self):
        # Sobreposição semi-transparente
        s = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        TELA.blit(s, (0, 0))
        
        # Mensagem
        gameover = FONTE_GRANDE.render("GAME OVER", True, VERMELHO)
        TELA.blit(gameover, (LARGURA // 2 - gameover.get_width() // 2, 150))
        
        # Pontuação
        pontos = FONTE_MEDIA.render(f"Pontos: {self.pontos}", True, BRANCO)
        TELA.blit(pontos, (LARGURA // 2 - pontos.get_width() // 2, 250))
        
        # Melhor pontuação
        melhor = FONTE_MEDIA.render(f"Melhor: {self.melhor_pontuacao}", True, BRANCO)
        TELA.blit(melhor, (LARGURA // 2 - melhor.get_width() // 2, 300))
        
        # Instruções
        reiniciar = FONTE_MEDIA.render("Pressione ESPAÇO para jogar", True, BRANCO)
        TELA.blit(reiniciar, (LARGURA // 2 - reiniciar.get_width() // 2, 400))
        
        menu = FONTE_PEQUENA.render("Pressione M para voltar ao menu", True, BRANCO)
        TELA.blit(menu, (LARGURA // 2 - menu.get_width() // 2, 450))

def main():
    jogo = Jogo()
    relogio = pygame.time.Clock()
    
    # if sons.musica: sons.musica.play(-1)  # -1 para loop infinito
    
    while True:
        relogio.tick(60)  # 60 FPS
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    if jogo.estado == "menu":
                        jogo.estado = "jogando"
                    elif jogo.estado == "jogando":
                        jogo.passaro.pular()
                    elif jogo.estado == "gameover":
                        jogo.reset()
                        jogo.estado = "jogando"
                
                if evento.key == pygame.K_m and jogo.estado == "gameover":
                    jogo.reset()
                    jogo.estado = "menu"
        
        if jogo.estado == "jogando":
            jogo.atualizar()
        
        jogo.desenhar()
        pygame.display.update()

if __name__ == "__main__":
    main()