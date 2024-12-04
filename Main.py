import pygame
import math
from screeninfo import get_monitors

class GameConstants:
    # Estados
    STATE_FALLING = "Cayendo"
    STATE_DIGGING = "Cavando"
    STATE_IDLE = "Quieto"
    
    # Colores
    COLORS = {
        'RED': (255, 0, 0),
        'BLACK': (0, 0, 0),
        'WHITE': (255, 255, 255),
        'BLUE': (0, 0, 255),
        'GREEN': (0, 255, 0)
    }
    
    # Physics
    GRAVITY_FACTOR = 5
    ACCELERATION_FACTOR = 5
    BRAKE_FACTOR = 13
    MAX_SPEED_FACTOR = 15
    JUMP_FORCE = 20
    
    # Display
    FPS = 60
    MENU_OVERLAY_ALPHA = 1
    MENU_OVERLAY_COLOR = (190, 190, 190)
    TILE_DIVISOR = 30

class AudioConfig:
    """Configuration class for audio settings"""
    def __init__(self):
        self.master_volume = 1.0  # 0.0 to 1.0
        self.sfx_volume = 0.7     # Volumen efectos de sonido
        self.music_volume = 0.5   # Volumen música
        self.enabled = True       # Audio habilitado/deshabilitado
        
        # Configuración individual de sonidos
        self.sound_configs = {
            'jump': {
                'path': 'assets/Audio/SFX_Jump.wav',
                'volume': 0.5,    # Volumen relativo al sfx_volume
                'delay': 300,     # Delay en milisegundos
                'channel': 0      # Canal de audio
            },
            'dig': {
                'path': 'assets/Audio/SFX_Dig.wav',
                'volume': 0.3,
                'delay': 1000,
                'channel': 1
            }
        }
        
        # Valores por defecto
        self.default_delay = 200
        self.default_volume = 0.5
        self.default_channel = 0

class ScreenData:
    """Auxiliary class to handle screen data and calculations"""
    def __init__(self):
        self.total_width = 0
        self.total_height = 0
        self.mid_y = 0
        self.mid_x = 0
        self.tile_size = 0
        self.border_x = 0
        self.border_y = 0
        self.tiles_x = 0
        self.tiles_y = 0
        self.display_surface = None

    def calculate_tile_size(self):
        """Calculate tile size and related measurements"""
        self.tile_size = self.total_width // GameConstants.TILE_DIVISOR
        self.tiles_x = self.total_width // self.tile_size
        self.tiles_y = self.total_height // self.tile_size
        self.border_x = self.total_width - (self.tiles_x * self.tile_size)
        self.border_y = self.total_height - (self.tiles_y * self.tile_size)

    def calculate_position(self, x_tiles, y_tiles):
        """Calculate pixel position from tile coordinates"""
        return (
            math.ceil(self.tile_size * x_tiles) + self.border_x // 2,
            math.ceil(self.tile_size * y_tiles) + self.border_y // 2
        )

    def get_data(self, *args):
        """Get screen data by parameter names"""
        data = {
            "width": self.total_width,
            "height": self.total_height,
            "mid_x": self.mid_x,
            "mid_y": self.mid_y,
            "tile_size": self.tile_size,
            "border_x": self.border_x,
            "border_y": self.border_y,
            "tiles_x": self.tiles_x,
            "tiles_y": self.tiles_y,
            "display": self.display_surface
        }
        return [data[arg] for arg in args if arg in data] if len(args) > 1 else data[args[0]]

# Clase para manejar cada pantalla
class Pantalla:
    def __init__(self, width, height, title="Screen"):
        self.screen_data = ScreenData()
        self.width = width
        self.height = height
        pygame.display.set_caption(title)
        self.display_surface = self._select_screen(1)
        self._calculate_dimensions()

    def _calculate_dimensions(self):
        self.screen_data.calculate_tile_size()

    def _select_screen(self, screen_index):
        monitors = get_monitors()
        if (screen_index < 0 or screen_index >= len(monitors)):
            screen_index = 0
            
        self.screen_data.total_width = monitors[screen_index].width
        self.screen_data.total_height = monitors[screen_index].height
        self.screen_data.mid_y = self.screen_data.total_height // 2
        self.screen_data.mid_x = self.screen_data.total_width // 2
        
        self.screen_data.display_surface = pygame.display.set_mode(
            (self.screen_data.total_width, self.screen_data.total_height),
            pygame.FULLSCREEN,
            display=screen_index
        )
        return self.screen_data.display_surface

    def get_screen_data(self, *args):
        return self.screen_data.get_data(*args)

    def actualizar_juego(self, **kwargs):
        self.display_surface.fill(GameConstants.COLORS['BLACK'])

        for obj in kwargs.values():
            obj.dibujar(self)
        
        pygame.display.flip()

    def actualizar_menu(self):
        # Crear una superficie con transparencia
        overlay = pygame.Surface((self.screen_data.total_width, self.screen_data.total_height), pygame.SRCALPHA)
        overlay.fill((*GameConstants.MENU_OVERLAY_COLOR, GameConstants.MENU_OVERLAY_ALPHA))  # Rellenar con negro y 50% de transparencia (128 en el canal alfa)
        self.display_surface.blit(overlay, (0, 0))

        pygame.display.flip()

    def detener(self):
        pygame.display.quit()

# Clase para manejar el personaje
class CollisionState:
    """Class to handle collision states"""
    def __init__(self):
        self.body = False
        self.top = False
        self.bottom = False
        self.platform = None

class CollisionHandler:
    """Class to handle collision detection and response"""
    @staticmethod
    def check_collisions(character_rects, platforms):
        state = CollisionState()
        
        for platform in platforms:
            if character_rects['main'].colliderect(platform):
                state.body = True
            if character_rects['top'].colliderect(platform):
                state.top = True
            if character_rects['bottom'].colliderect(platform):
                state.bottom = True
                state.platform = platform
                
        return state

    @staticmethod
    def update_character_state(character, collision_state, keys):
        """Update character state based on collisions"""
        if collision_state.body:
            if (character.estado_gravedad in [GameConstants.STATE_DIGGING, GameConstants.STATE_FALLING] and 
                keys[pygame.K_DOWN]):
                character.estado_gravedad = GameConstants.STATE_DIGGING
            else:
                character.estado_gravedad = GameConstants.STATE_IDLE
            
        if collision_state.top:
            character.saltando(True)
        
        if collision_state.bottom:
            character.saltando(True)
            character.cavando(True)
            character.ensima_Colision = collision_state.platform
        else:
            character.estado_gravedad = GameConstants.STATE_FALLING
            character.cavando(False)

class Personaje:
    salto = False
    cavar = False
    ensima_Colision = None  # Corrected typo here
    estado_gravedad = GameConstants.STATE_FALLING
    velocidad_x = 0
    velocidad_y = 0

    def __init__(self, x, y, tamaño):
        self.rect = pygame.Rect(x, y, tamaño, tamaño)
        self.arriba_rect = pygame.Rect(x, y - tamaño / 2, tamaño, tamaño / 2)
        self.abajo_rect = pygame.Rect(x, y + tamaño, tamaño, tamaño / 2)
        self.derecha_rect = pygame.Rect((x + tamaño), y, tamaño / 2, tamaño)
        self.izquierda_rect = pygame.Rect(x - tamaño / 2, y, tamaño / 2, tamaño)
        self.tamaño = tamaño
        self.velocidad_maxima = tamaño / GameConstants.MAX_SPEED_FACTOR
        self.gravedad = tamaño / GameConstants.GRAVITY_FACTOR
        self.freno = tamaño / GameConstants.BRAKE_FACTOR
        self.aceleracion = tamaño / GameConstants.ACCELERATION_FACTOR
    
    def get_rect(self):
        return self.rect

    def saltando(self, nuevo_estado):
        self.salto = nuevo_estado
    
    def cavando(self, nuevo_estado):
        self.cavar = nuevo_estado

    def get_collision_rects(self):
        """Get all collision rectangles"""
        return {
            'main': self.rect,
            'top': self.arriba_rect,
            'bottom': self.abajo_rect
        }

    def calcular_colision(self, controlador, teclas):
        collision_state = CollisionHandler.check_collisions(
            self.get_collision_rects(), 
            controlador.get_rects()
        )
        CollisionHandler.update_character_state(self, collision_state, teclas)
                    
    def actualizar_posicion_rects(self):
        """Actualiza la posición de todos los rectángulos del personaje"""
        self.arriba_rect.x = self.rect.x
        self.arriba_rect.y = self.rect.y - self.tamaño / 2
        self.abajo_rect.x = self.rect.x
        self.abajo_rect.y = self.rect.y + self.tamaño
        self.derecha_rect.x = self.rect.x + self.tamaño
        self.derecha_rect.y = self.rect.y
        self.izquierda_rect.x = self.rect.x - self.tamaño/2
        self.izquierda_rect.y = self.rect.y

    def reiniciar_posicion(self, x, y):
        """Reinicia la posición del personaje y todos sus rectángulos"""
        self.velocidad_x = 0
        self.velocidad_y = 0
        self.rect.x = x
        self.rect.y = y
        self.actualizar_posicion_rects()

    def accion_gravedad(self):
        if self.estado_gravedad == GameConstants.STATE_FALLING:
            self.velocidad_y += self.gravedad
        elif self.estado_gravedad == GameConstants.STATE_DIGGING:
            self.velocidad_y -= (self.rect.y - (self.ensima_Colision.y-self.tamaño/2))*int(self.tamaño/4)
            if -0.01 < self.velocidad_y < 0.01:
                self.rect.y = self.ensima_Colision.y - self.tamaño
                self.actualizar_posicion_rects()
        elif self.estado_gravedad == GameConstants.STATE_IDLE:
            self.velocidad_y = 0
            self.rect.y = self.ensima_Colision.y - self.tamaño
            self.actualizar_posicion_rects()

    def muerto(self, pantalla=Pantalla):
        datos_pantalla = pantalla.get_screen_data(
            "tiles_y", 
            "tiles_x",
            "border_x",
            "border_y",
            "tile_size"
            )
        inicio_X = datos_pantalla[2] // 2 
        inicio_Y = datos_pantalla[3] // 2
        tamaño_X = datos_pantalla[4] * datos_pantalla[1]
        tamaño_Y = datos_pantalla[4] * datos_pantalla[0]
        if self.rect.y > tamaño_Y+self.tamaño:
            self.reiniciar_posicion(inicio_X + tamaño_X//2, inicio_Y + tamaño_Y//2)

    def mover(self, teclas, delta_time, pantalla):
        self.muerto(pantalla)
        self.accion_gravedad()
        self.frenar(teclas)

        velocidad_escalada_x = int(self.velocidad_x * delta_time * 10) / 10
        velocidad_escalada_y = int(self.velocidad_y * delta_time * 10) / 10

        # Actualizar velocidades según teclas
        self.actualizar_velocidades(teclas, velocidad_escalada_x, velocidad_escalada_y)

        # Actualizar posiciones
        self.rect.x += velocidad_escalada_x
        self.rect.y += velocidad_escalada_y
        self.actualizar_posicion_rects()

    def actualizar_velocidades(self, teclas, velocidad_escalada_x, velocidad_escalada_y):
        """Actualiza las velocidades según las teclas presionadas"""
        resource_manager = ResourceManager()
        if teclas[pygame.K_LEFT] and self.velocidad_maxima * -1 <= velocidad_escalada_x:
            self.velocidad_x -= self.aceleracion
        if teclas[pygame.K_RIGHT] and self.velocidad_maxima >= velocidad_escalada_x:
            self.velocidad_x += self.aceleracion
        if teclas[pygame.K_UP] and self.velocidad_maxima * -1 <= velocidad_escalada_y and self.salto:
            resource_manager.play_sound('jump')
            self.salto = False
            self.estado_gravedad = GameConstants.STATE_FALLING
            self.velocidad_y -= self.aceleracion * GameConstants.JUMP_FORCE
        if teclas[pygame.K_DOWN] and self.velocidad_maxima >= velocidad_escalada_y and self.cavar:
            resource_manager.play_sound('dig')
            self.cavar = False
            self.estado_gravedad = GameConstants.STATE_DIGGING
            self.velocidad_y += self.aceleracion * GameConstants.JUMP_FORCE

    def frenar(self, teclas):
        if not teclas[pygame.K_LEFT] and not teclas[pygame.K_RIGHT] and self.velocidad_x != 0:
            if self.velocidad_x > 0:
                if not self.salto:
                    self.velocidad_x -= self.freno/10
                else:
                    self.velocidad_x = int(self.velocidad_x/10)*10                
                    self.velocidad_x -= self.freno
            elif self.velocidad_x < 0:
                if not self.salto:
                    self.velocidad_x += self.freno/10
                else:
                    self.velocidad_x = int(self.velocidad_x/10)*10
                    self.velocidad_x += self.freno
        else:
            if self.velocidad_x > 0:
                self.velocidad_x -= int(self.freno/10)
            elif self.velocidad_x < 0:
                self.velocidad_x += int(self.freno/10)
        
        if not teclas[pygame.K_UP] and not teclas[pygame.K_DOWN] and self.velocidad_y != 0:
            if self.velocidad_y > 0:
                self.velocidad_y -= int(self.freno/1.5)
            elif self.velocidad_y < 0:
                self.velocidad_y += int(self.freno)
        else:
            if self.velocidad_y > 0:
                self.velocidad_y -= int(self.freno/4)
            elif self.velocidad_y < 0:
                self.velocidad_y += int(self.freno/4)
        

    
    def dibujar(self, pantalla=Pantalla):
        resource_manager = ResourceManager()
        pantalla= pantalla.get_screen_data("display")
        player_image = resource_manager.get_scaled_sprite('player', self.tamaño, self.tamaño, 0, 0)
        
        if player_image:
            pantalla.blit(player_image, self.rect)
        else:
            pygame.draw.rect(pantalla, GameConstants.COLORS['RED'], self.rect)
        #probar hitbox
        pygame.draw.rect(pantalla, GameConstants.COLORS['BLUE'], self.arriba_rect)
        pygame.draw.rect(pantalla, GameConstants.COLORS['BLUE'], self.abajo_rect)
        pygame.draw.rect(pantalla, GameConstants.COLORS['BLUE'], self.derecha_rect)
        pygame.draw.rect(pantalla, GameConstants.COLORS['BLUE'], self.izquierda_rect)


# Clase para manejar el fondo
class Fondo:
    def __init__(self):
        pass

    def dibujar(self, pantalla=Pantalla):
        datos_pantalla = pantalla.get_screen_data(
            "tiles_y", 
            "tiles_x",
            "border_x",
            "border_y",
            "tile_size",
            "display"
            )
        
        for y in range(datos_pantalla[0]):
            for x in range(datos_pantalla[1]):
                 if (x + y) % 2 == 0:
                    rect = pygame.Rect(
                        datos_pantalla[2] // 2 + x * datos_pantalla[4],
                        datos_pantalla[3] // 2 + y * datos_pantalla[4],
                        datos_pantalla[4],
                        datos_pantalla[4]
                    )
                    pygame.draw.rect(datos_pantalla[5], GameConstants.COLORS['WHITE'], rect)


# Clase para manejar Plataformas
class Plataforma:
    def __init__(self, **kwargs):
        self.tipo = kwargs.get('tipo', 'default')
        self.alto = kwargs.get('alto', 0)
        self.ancho = kwargs.get('ancho', 0)
        self.posicion_X = kwargs.get('posicion_X', 0)
        self.posicion_Y = kwargs.get('posicion_Y', 0)
        self.visible = kwargs.get('visible', True)
        self.rect = pygame.Rect(self.posicion_X, self.posicion_Y, self.ancho, self.alto)

    def get_rect(self):
        return self.rect
    
    def switch_visible(self):
        self.visible = not self.visible

    """def _make_plataform(self, pantalla=Pantalla):
        resource_manager = ResourceManager()
        tamaño = pantalla.get_screen_data("tile_size")
        platform_esquina_left = resource_manager.get_scaled_sprite('platform_', tamaño, tamaño, 0, 0)
        platform_esquina_right = resource_manager.get_scaled_sprite('platform_', tamaño, tamaño, 0, 2)
        platform_row = resource_manager.get_scaled_sprite('platform_', tamaño, tamaño, 0, 1)
        platform_col = resource_manager.get_scaled_sprite('platform_', tamaño, tamaño, 0, 3)
        return pantalla.get_screen_data("tiles_x", "tiles_y")"""

    def dibujar(self, pantalla=Pantalla):
        if self.visible:
            tamaño = pantalla.get_screen_data("tile_size")
            pantalla = pantalla.get_screen_data("display")
            
            #platform = _make_plataform(pantalla)
            resource_manager = ResourceManager()
            
            platform_row = resource_manager.get_scaled_sprite('platform_rock', tamaño, tamaño, 0, 0)

            if platform_row:
                pantalla.blit(platform_row, self.rect)
            else:
                pygame.draw.rect(pantalla, GameConstants.COLORS['GREEN'], self.rect)

class controlador_plataformas:
    def __init__(self):
        self.plataformas = []

    def agregar_plataforma(self, plataforma):
        self.plataformas.append(plataforma)

    def remover_plataforma(self, plataforma):
        if plataforma in self.plataformas:
            self.plataformas.remove(plataforma)

    def get_rects(self):
        return [plataforma.get_rect() for plataforma in self.plataformas]

    def dibujar(self, pantalla=Pantalla):
        for plataforma in self.plataformas:
            plataforma.dibujar(pantalla)

class PlatformConfig:
    """Configuration class for platform creation"""
    def __init__(self, tipo, alto_factor, ancho_factor, pos_x, pos_y):
        self.tipo = tipo
        self.alto_factor = alto_factor  # Factor multiplicador para alto
        self.ancho_factor = ancho_factor  # Factor multiplicador para ancho
        self.pos_x = pos_x  # Posición X en baldosas
        self.pos_y = pos_y  # Posición Y en baldosas

def crear_plataformas(controlador=controlador_plataformas, pantalla=Pantalla):
    screen_data = pantalla.get_screen_data(
        "mid_y", "mid_x", "tile_size", 
        "border_x", "border_y", "tiles_x", "tiles_y"
    )
    
    # Configuración de todas las plataformas
    plataformas_config = [
        PlatformConfig("suelo", 4, screen_data[5]/2, screen_data[6]/4, screen_data[6]*3/4),
        PlatformConfig("voladora", 1, 3, 6, 10),
        PlatformConfig("prueba1", 0.5, 4, 12, 9),
        PlatformConfig("prueba2", 1, 4, 25, 14)
    ]

    # Crear y agregar cada plataforma
    for config in plataformas_config:
        x, y = pantalla.screen_data.calculate_position(config.pos_x, config.pos_y)
        
        plataforma = Plataforma(
            tipo=config.tipo,
            alto=screen_data[2] * config.alto_factor,
            ancho=screen_data[2] * config.ancho_factor,
            posicion_X=x,
            posicion_Y=y
        )
        controlador.agregar_plataforma(plataforma)

    return controlador

class GameStateManager:
    """Manages game states and transitions"""
    def __init__(self, pantalla, jugador, controlador):
        self.pantalla = pantalla
        self.jugador = jugador
        self.controlador = controlador
        self.clock = pygame.time.Clock()
        self.current_state = "menu"
        self.fondo = Fondo()
        self.running = True
        self.resource_manager = ResourceManager()
        self.resource_manager.load_resources()

    def handle_menu(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return True
        
        teclas = pygame.key.get_pressed()
        self.pantalla.actualizar_menu()

        if teclas[pygame.K_ESCAPE]:
            pygame.time.wait(200)
            self.current_state = "playing"
        elif teclas[pygame.K_BACKSPACE]:
            return True
        return False

    def handle_playing(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return True

        delta_time = self.clock.tick(GameConstants.FPS) / 1000.0
        teclas = pygame.key.get_pressed()

        if teclas[pygame.K_ESCAPE]:
            pygame.time.wait(200)
            self.current_state = "menu"
            return False

        self.jugador.calcular_colision(self.controlador, teclas)
        self.jugador.mover(teclas, delta_time, self.pantalla)
        self.pantalla.actualizar_juego(
            fondo=self.fondo,
            personaje=self.jugador,
            plataforma=self.controlador,
        )
        return False

    def run(self):
        self.controlador = crear_plataformas(self.controlador, self.pantalla)
        
        while self.running:
            if self.current_state == "menu":
                self.running = not self.handle_menu()
            elif self.current_state == "playing":
                self.running = not self.handle_playing()

        return True

class SpriteSheet:
    """Handles sprite sheets and tile cutting"""
    def __init__(self, surface):
        self.sheet = surface

    def get_sprite(self, x, y, width, height):
        """Get a single sprite from the sheet"""
        sprite = pygame.Surface((width, height), pygame.SRCALPHA)
        sprite.blit(self.sheet, (0, 0), (x, y, width, height))
        return sprite
    
    def get_sprite_row(self, y, sprite_width, sprite_height, count):
        """Get a row of sprites"""
        return [self.get_sprite(i * sprite_width, y, sprite_width, sprite_height) 
                for i in range(count)]
    
    def get_sprite_grid(self, sprite_width, sprite_height, rows, cols, start_row=0, start_col=0):
        """Get a grid of sprites starting from specific row and column"""
        sprites = []
        for y in range(rows):
            row = []
            for x in range(cols):
                sprite = self.get_sprite(
                    (x + start_col) * sprite_width, 
                    (y + start_row) * sprite_height, 
                    sprite_width, 
                    sprite_height
                )
                row.append(sprite)
            sprites.append(row)
        return sprites

class ResourceManager:
    """Manages game resources like images and sounds"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ResourceManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        self.images = {}
        self.sounds = {}
        self.sound_delays = {}  # Almacena el tiempo de último uso de cada sonido
        self.spritesheets = {}  # Para almacenar spritesheets
        self.sprites = {}       # Para almacenar sprites individuales
        self.audio_config = AudioConfig()
        self._initialized = True

    

    def play_sound(self, key):
        """Play a sound by key with configurable delay control"""
        if not self.audio_config.enabled:
            return

        current_time = pygame.time.get_ticks()
        last_played = self.sound_delays.get(key, 0)
        
        sound_config = self.audio_config.sound_configs.get(key, {
            'delay': self.audio_config.default_delay,
            'channel': self.audio_config.default_channel,
            'volume': self.audio_config.default_volume
        })
        
        if current_time - last_played >= sound_config['delay']:
            sound = self.get_sound(key)
            if sound:
                volume = (self.audio_config.master_volume * 
                         self.audio_config.sfx_volume * 
                         sound_config['volume'])
                sound.set_volume(volume)
                sound.play()
                self.sound_delays[key] = current_time

    

    def load_resources(self):
        """Load all game resources"""
        self._load_images()
        self._load_sounds()
        
    def _load_images(self):
        """Load all game images"""
        # Cargar imágenes normales
        image_paths = {
            'background': 'assets/Texturas/background.png'
        }
        
        # Cargar y cortar spritesheets
        spritesheet_configs = {
            'player': {
                'path': 'assets/Texturas/Jugador.png',
                'sprite_width': 16,
                'sprite_height': 16,
                'rows': 2,
                'cols': 2,
                'start_row': 0,  # Fila inicial para recortar
                'start_col': 0   # Columna inicial para recortar
            },
            'platform': {
                'path': 'assets/Texturas/Plataformas.png',
                'sprite_width': 8,
                'sprite_height': 8,
                'rows': 0,
                'cols': 0,
                'start_row': 0, 
                'start_col': 0   
            }
        }
        
        # Cargar imágenes normales
        for key, path in image_paths.items():
            try:
                self.images[key] = pygame.image.load(path).convert_alpha()
            except (pygame.error, FileNotFoundError):
                print(f"Warning: Could not load image {path}")
                self.images[key] = self._create_fallback_surface(32, 32)

        # Cargar y procesar spritesheets
        for key, config in spritesheet_configs.items():
            try:
                sheet_surface = pygame.image.load(config['path']).convert_alpha()
                self.spritesheets[key] = SpriteSheet(sheet_surface)
                self.sprites[key] = self.spritesheets[key].get_sprite_grid(
                    config['sprite_width'],
                    config['sprite_height'],
                    config['rows'],
                    config['cols'],
                    config.get('start_row', 0),  # Usar 0 como valor por defecto
                    config.get('start_col', 0)   # Usar 0 como valor por defecto
                )
            except (pygame.error, FileNotFoundError):
                print(f"Warning: Could not load spritesheet {config['path']}")
                self.sprites[key] = [[self._create_fallback_surface(
                    config['sprite_width'], 
                    config['sprite_height']
                )]]

    def _create_fallback_surface(self, width, height):
        """Create a fallback surface with checkerboard pattern"""
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        surface.fill(GameConstants.COLORS['RED'])
        return surface

    def get_image(self, key):
        """Get an image by key"""
        return self.images.get(key)
    
    def get_sound(self, key):
        """Get a sound by key"""
        return self.sounds.get(key)
    
    def update_volumes(self):
        """Update all sound volumes based on current configuration"""
        for key, sound in self.sounds.items():
            if sound and key in self.audio_config.sound_configs:
                config = self.audio_config.sound_configs[key]
                volume = (self.audio_config.master_volume * 
                         self.audio_config.sfx_volume * 
                         config['volume'])
                sound.set_volume(volume)

    def set_master_volume(self, volume):
        """Set master volume and update all sounds"""
        self.audio_config.master_volume = max(0.0, min(1.0, volume))
        self.update_volumes()

    def set_sfx_volume(self, volume):
        """Set SFX volume and update all sounds"""
        self.audio_config.sfx_volume = max(0.0, min(1.0, volume))
        self.update_volumes()

    def toggle_audio(self):
        """Toggle audio on/off"""
        self.audio_config.enabled = not self.audio_config.enabled
        if not self.audio_config.enabled:
            pygame.mixer.pause()
        else:
            pygame.mixer.unpause()

    def get_sprite(self, key, row=0, col=0):
        """Get a specific sprite from a spritesheet"""
        if key in self.sprites:
            try:
                return self.sprites[key][row][col]
            except IndexError:
                print(f"Warning: Invalid sprite indices for {key}: row={row}, col={col}")
                return self._create_fallback_surface(32, 32)
        return None

    def _load_sounds(self):
        """Load all game sounds and configure volumes"""
        for key, config in self.audio_config.sound_configs.items():
            try:
                sound = pygame.mixer.Sound(config['path'])
                # Aplicar volumen combinado (master * sfx * sound)
                volume = (self.audio_config.master_volume * 
                         self.audio_config.sfx_volume * 
                         config['volume'])
                sound.set_volume(volume)
                self.sounds[key] = sound
            except (pygame.error, FileNotFoundError):
                print(f"Warning: Could not load sound {config['path']}")

    def get_scaled_sprite(self, key, width, height, row=0, col=0):
        """Get a sprite scaled to specified dimensions"""
        sprite = self.get_sprite(key, row, col)
        if sprite:
            return pygame.transform.scale(sprite, (width, height))
        return None

    def create_combined_surface(self, key, tile_width, tile_height, rows, cols, start_row=0, start_col=0):
        """Create a combined surface from multiple tiles"""
        combined_surface = pygame.Surface((tile_width * cols, tile_height * rows), pygame.SRCALPHA)
        for row in range(rows):
            for col in range(cols):
                tile = self.get_scaled_sprite(key, tile_width, tile_height, start_row + row, start_col + col)
                if tile:
                    combined_surface.blit(tile, (col * tile_width, row * tile_height))
        return combined_surface

# Modificar la función main para usar GameStateManager
def main():
    pygame.init()
    pygame.mixer.init()  # Inicializar el sistema de sonido
    
    pantalla_principal = Pantalla(800, 600, "Pantalla Principal")
    tamaño_baldosa = pantalla_principal.get_screen_data("tile_size")
    controlador = controlador_plataformas()
    jugador = Personaje(pantalla_principal.get_screen_data("mid_x"), 300, tamaño_baldosa)

    try:
        game_manager = GameStateManager(pantalla_principal, jugador, controlador)
        game_manager.run()
    except KeyboardInterrupt:
        print("Interrupción del teclado detectada. Saliendo del juego...")
    finally:
        pantalla_principal.detener()
        pygame.quit()

if __name__ == "__main__":
    main()

