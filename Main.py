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
    MENU_OVERLAY_ALPHA = 20
    MENU_OVERLAY_COLOR = (200, 200, 200)
    TILE_DIVISOR = 30
    
    # UI Constants
    UI_MARGIN = 20  # Margen desde los bordes
    UI_HEALTH_WIDTH = 200  # Ancho de la barra de vida
    UI_HEALTH_HEIGHT = 30  # Alto de la barra de vida
    UI_MARGIN_BOTTOM = 50  # Nueva constante para margen inferior
    PLAYER_MAX_HEALTH = 300
    PLAYER_RESPAWN_DAMAGE = 100  # Renombrado de PLAYER_DAMAGE_FALL

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
        """Get screen data using method chaining"""
        if len(args) == 1:
            return self.screen_data.get_data(args[0])
        return self.screen_data.get_data(*args)

    def actualizar_juego(self, **kwargs):
        """Update game display with all game objects"""
        self._clear_screen()
        self._draw_all_objects(kwargs)
        self._update_display()

    def _clear_screen(self):
        """Clear screen with background color"""
        self.display_surface.fill(GameConstants.COLORS['BLACK'])

    def _draw_all_objects(self, game_objects):
        """Draw all game objects in the correct order"""
        # Dibujar fondo primero
        if 'fondo' in game_objects:
            game_objects['fondo'].dibujar(self)

        # Dibujar jugadores que no están cavando
        if 'jugadores' in game_objects:
            for jugador in game_objects['jugadores']:
                if jugador.estado_gravedad == GameConstants.STATE_DIGGING:
                    jugador.dibujar(self)

        # Dibujar plataformas
        if 'plataforma' in game_objects:
            game_objects['plataforma'].dibujar(self)

        # Dibujar jugadores que están cavando
        if 'jugadores' in game_objects:
            for jugador in game_objects['jugadores']:
                if jugador.estado_gravedad != GameConstants.STATE_DIGGING:
                    jugador.dibujar(self)

        # Dibujar HUD al final
        if 'hud' in game_objects:
            game_objects['hud'](self)

    def _update_display(self):
        """Update the display"""
        pygame.display.flip()

    def actualizar_menu(self):
        """Update menu display with overlay"""
        #self._clear_screen()#
        self._draw_menu_overlay()
        self._update_display()

    def _draw_menu_overlay(self):
        """Draw semi-transparent menu overlay"""
        overlay = pygame.Surface(
            (self.screen_data.total_width, self.screen_data.total_height), 
            pygame.SRCALPHA
        )
        overlay.fill((*GameConstants.MENU_OVERLAY_COLOR, GameConstants.MENU_OVERLAY_ALPHA))
        self.display_surface.blit(overlay, (0, 0))

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
            # Usar los controles específicos del jugador para verificar la tecla abajo
            down_key = character.controls.get_key('down')
            if (character.estado_gravedad in [GameConstants.STATE_DIGGING, GameConstants.STATE_FALLING] and 
                keys[down_key]):  # Cambiar pygame.K_DOWN por down_key
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
    """Player character with configurable controls and physics"""
    def __init__(self, x, y, tamaño, controls=None, player_id=1):
        self._init_physics(x, y, tamaño)
        self._init_state(player_id)
        self._init_controls(controls, player_id)
        self._init_stats()

    def _init_physics(self, x, y, tamaño):
        """Initialize physics-related attributes"""
        self.rect = pygame.Rect(x, y, tamaño, tamaño)
        self.tamaño = tamaño
        self._create_collision_rects(x, y)
        self._setup_movement_params()
        
    def _create_collision_rects(self, x, y):
        """Create collision detection rectangles"""
        h = self.tamaño / 2
        self.arriba_rect = pygame.Rect(x, y - h, self.tamaño, h)
        self.abajo_rect = pygame.Rect(x, y + self.tamaño, self.tamaño, h)
        self.derecha_rect = pygame.Rect(x + self.tamaño, y, h, self.tamaño)
        self.izquierda_rect = pygame.Rect(x - h, y, h, self.tamaño)

    def _setup_movement_params(self):
        """Setup movement and physics parameters"""
        self.velocidad_maxima = self.tamaño / GameConstants.MAX_SPEED_FACTOR
        self.gravedad = self.tamaño / GameConstants.GRAVITY_FACTOR
        self.freno = self.tamaño / GameConstants.BRAKE_FACTOR
        self.aceleracion = self.tamaño / GameConstants.ACCELERATION_FACTOR
        self.velocidad_x = 0
        self.velocidad_y = 0

    def _init_state(self, player_id):
        """Initialize state variables"""
        self.player_id = player_id
        # Configurar sprite según player_id
        self.sprite_config = {
            1: {'row': 0, 'col': 0},  # Jugador 1: sprite en (0,0)
            2: {'row': 1, 'col': 1}   # Jugador 2: sprite en (1,1)
        }.get(player_id, {'row': 0, 'col': 0})  # Default a (0,0) si no es 1 o 2
        
        self.salto = False
        self.cavar = False
        self.ensima_Colision = None
        self.estado_gravedad = GameConstants.STATE_FALLING

    def _init_controls(self, controls, player_id):
        """Initialize player controls"""
        self.controls = controls or PlayerControls.get_default_controls(player_id)  
        
    def _init_stats(self):
        """Initialize player stats"""
        self.health = GameConstants.PLAYER_MAX_HEALTH

    def actualizar_velocidades(self, teclas, velocidad_escalada_x, velocidad_escalada_y):
        """Update velocities based on input"""
        self._handle_horizontal_movement(teclas, velocidad_escalada_x)
        self._handle_vertical_movement(teclas, velocidad_escalada_y)

    def _handle_horizontal_movement(self, teclas, velocidad_escalada_x):
        """Handle left/right movement"""
        if (teclas[self.controls.get_key('left')] and 
            self.velocidad_maxima * -1 <= velocidad_escalada_x):
            self.velocidad_x -= self.aceleracion
            
        if (teclas[self.controls.get_key('right')] and 
            self.velocidad_maxima >= velocidad_escalada_x):
            self.velocidad_x += self.aceleracion

    def _handle_vertical_movement(self, teclas, velocidad_escalada_y):
        """Handle jumping and digging"""
        resource_manager = ResourceManager()
        
        # Jumping
        if self._can_jump(teclas, velocidad_escalada_y):
            self._perform_jump(resource_manager)
            
        # Digging
        if self._can_dig(teclas, velocidad_escalada_y):
            self._perform_dig(resource_manager)

    def _can_jump(self, teclas, velocidad_escalada_y):
        return (teclas[self.controls.get_key('up')] and 
                self.velocidad_maxima * -1 <= velocidad_escalada_y and 
                self.salto)

    def _can_dig(self, teclas, velocidad_escalada_y):
        return (teclas[self.controls.get_key('down')] and 
                self.velocidad_maxima >= velocidad_escalada_y and 
                self.cavar)

    def _perform_jump(self, resource_manager):
        resource_manager.play_sound('jump')
        self.salto = False
        self.estado_gravedad = GameConstants.STATE_FALLING
        self.velocidad_y -= self.aceleracion * GameConstants.JUMP_FORCE

    def _perform_dig(self, resource_manager):
        resource_manager.play_sound('dig')
        self.cavar = False
        self.estado_gravedad = GameConstants.STATE_DIGGING
        self.velocidad_y += self.aceleracion * GameConstants.JUMP_FORCE

    def frenar(self, teclas):
        """Apply braking forces"""
        self._brake_horizontal(teclas)
        self._brake_vertical(teclas)

    def _brake_horizontal(self, teclas):
        """Apply horizontal braking"""
        left_key = self.controls.get_key('left')
        right_key = self.controls.get_key('right')
        
        if not teclas[left_key] and not teclas[right_key] and self.velocidad_x != 0:
            self._apply_horizontal_brake()
        else:
            self._apply_horizontal_resistance()

    def _brake_vertical(self, teclas):
        """Apply vertical braking"""
        up_key = self.controls.get_key('up')
        down_key = self.controls.get_key('down')
        
        if not teclas[up_key] and not teclas[down_key] and self.velocidad_y != 0:
            self._apply_vertical_brake()
        else:
            self._apply_vertical_resistance()

    def _apply_horizontal_brake(self):
        """Apply horizontal brake force"""
        if self.velocidad_x > 0:
            self.velocidad_x -= self.freno / 10 if not self.salto else self.freno
        elif self.velocidad_x < 0:
            self.velocidad_x += self.freno / 10 if not self.salto else self.freno

    def _apply_horizontal_resistance(self):
        """Apply horizontal resistance"""
        if self.velocidad_x > 0:
            self.velocidad_x -= int(self.freno / 10)
        elif self.velocidad_x < 0:
            self.velocidad_x += int(self.freno / 10)

    def _apply_vertical_brake(self):
        """Apply vertical brake force"""
        if self.velocidad_y > 0:
            self.velocidad_y -= int(self.freno / 1.5)
        elif self.velocidad_y < 0:
            self.velocidad_y += int(self.freno)

    def _apply_vertical_resistance(self):
        """Apply vertical resistance"""
        if self.velocidad_y > 0:
            self.velocidad_y -= int(self.freno / 4)
        elif self.velocidad_y < 0:
            self.velocidad_y += int(self.freno / 4)

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

    def mover(self, teclas, delta_time, pantalla):
        self._check_respawn(pantalla)
        self._update_physics(teclas)
        
        velocidad_escalada = self._scale_velocities(delta_time)
        self.actualizar_velocidades(teclas, *velocidad_escalada)
        self._update_position(velocidad_escalada)

    def _check_respawn(self, pantalla):
        """Check if player needs to respawn and apply respawn damage"""
        datos_pantalla = pantalla.get_screen_data(
            "tiles_y", "tiles_x", "border_x", 
            "border_y", "tile_size"
        )
        inicio_X = datos_pantalla[2] // 2 
        inicio_Y = datos_pantalla[3] // 2
        tamaño_X = datos_pantalla[4] * datos_pantalla[1]
        tamaño_Y = datos_pantalla[4] * datos_pantalla[0]
        
        if self.rect.y > tamaño_Y + self.tamaño:
            self.take_damage(GameConstants.PLAYER_RESPAWN_DAMAGE)
            self.reiniciar_posicion(inicio_X + tamaño_X//2, inicio_Y + tamaño_Y//2)

    def _update_physics(self, teclas):
        """Update physics state"""
        self.accion_gravedad()
        self.frenar(teclas)

    def _update_position(self, velocidades):
        """Update position based on scaled velocities"""
        self.rect.x += velocidades[0]
        self.rect.y += velocidades[1]
        self.actualizar_posicion_rects()

    def _scale_velocities(self, delta_time):
        """Scale velocities based on delta time"""
        scale_factor = delta_time * 10
        return (
            int(self.velocidad_x * scale_factor) / 10,
            int(self.velocidad_y * scale_factor) / 10
        )

    def take_damage(self, amount):
        self.health = max(0, self.health - amount)

    def heal(self, amount):
        self.health = min(GameConstants.PLAYER_MAX_HEALTH, self.health + amount)

    def get_health_percentage(self):
        return self.health / GameConstants.PLAYER_MAX_HEALTH

    def dibujar(self, pantalla=Pantalla):
        resource_manager = ResourceManager()
        display = pantalla.get_screen_data("display")
        
        player_image = resource_manager.get_scaled_sprite(
            'player', 
            self.tamaño, 
            self.tamaño, 
            self.sprite_config['row'], 
            self.sprite_config['col']
        )
        
        if player_image:
            display.blit(player_image, self.rect)
        else:
            pygame.draw.rect(display, GameConstants.COLORS['RED'], self.rect)
            
        #probar hitbox
        pygame.draw.rect(display, GameConstants.COLORS['BLUE'], self.arriba_rect)
        pygame.draw.rect(display, GameConstants.COLORS['BLUE'], self.abajo_rect)
        pygame.draw.rect(display, GameConstants.COLORS['BLUE'], self.derecha_rect)
        pygame.draw.rect(display, GameConstants.COLORS['BLUE'], self.izquierda_rect)


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
    def __init__(self, pantalla, jugadores, controlador, hud):
        self.pantalla = pantalla
        self._setup_game_objects(jugadores, controlador, hud)
        self._setup_game_state()

    def _setup_game_objects(self, jugadores, controlador, hud):
        """Initialize game objects"""
        self.jugadores = jugadores if isinstance(jugadores, list) else [jugadores]
        self.controlador = controlador
        self.hud = hud
        self.fondo = Fondo()
        self.resource_manager = ResourceManager()
        self.resource_manager.load_resources()

    def _setup_game_state(self):
        """Initialize game state variables"""
        self.clock = pygame.time.Clock()
        self.current_state = "menu"
        self.running = True
        self.controlador = crear_plataformas(self.controlador, self.pantalla)

    def run(self):
        """Main game loop"""
        while self.running:
            self.running = not self._handle_current_state()
        return True

    def _handle_current_state(self):
        """Handle current game state"""
        state_handlers = {
            "menu": self.handle_menu,
            "playing": self.handle_playing
        }
        return state_handlers.get(self.current_state, lambda: False)()

    def handle_menu(self):
        """Handle menu state"""
        if self._check_quit_event():
            return True

        teclas = pygame.key.get_pressed()
        self.pantalla.actualizar_menu()

        if teclas[pygame.K_ESCAPE]:
            self._transition_to_state("playing")
        elif teclas[pygame.K_BACKSPACE]:
            return True
        return False

    def handle_playing(self):
        """Handle playing state"""
        if self._check_quit_event():
            return True

        delta_time = self._update_time()
        teclas = pygame.key.get_pressed()

        if self._handle_escape_key(teclas):
            return False

        self._update_game_state(teclas, delta_time)
        self._render_game()
        return False

    def _check_quit_event(self):
        """Check for quit events"""
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return True
        return False
        
    def _transition_to_state(self, new_state):
        """Handle state transition"""
        pygame.time.wait(200)
        self.current_state = new_state

    def _handle_escape_key(self, teclas):
        """Handle escape key press"""
        if teclas[pygame.K_ESCAPE]:
            self._transition_to_state("menu")
            return True
        return False

    def _update_time(self):
        """Update game time"""
        return self.clock.tick(GameConstants.FPS) / 1000.0

    def _update_game_state(self, teclas, delta_time):
        """Update game state for all players"""
        for jugador in self.jugadores:
            self._update_player(jugador, teclas, delta_time)

    def _update_player(self, jugador, teclas, delta_time):
        """Update individual player state"""
        jugador.calcular_colision(self.controlador, teclas)
        jugador.mover(teclas, delta_time, self.pantalla)

    def _render_game(self):
        """Render game state"""
        self.pantalla.actualizar_juego(
            fondo=self.fondo,
            jugadores=self.jugadores,
            plataforma=self.controlador,
            hud=lambda p: self.hud.dibujar(p, self.jugadores)
        )

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

class HUD:
    """Heads Up Display for game interface"""
    def __init__(self, game_constants):
        self.constants = game_constants
        self._setup_colors()
        self._setup_rects()

    def _setup_colors(self):
        """Setup color references for better readability"""
        self.colors = {
            'background': self.constants.COLORS['RED'],
            'health': self.constants.COLORS['GREEN'],
            'border': self.constants.COLORS['WHITE']
        }

    def _setup_rects(self):
        """Initialize health bar rectangles for both players"""
        screen_width = pygame.display.get_surface().get_width()
        screen_height = pygame.display.get_surface().get_height()
        
        # Rectángulo jugador 1 (izquierda)
        self.background_rect_p1 = pygame.Rect(
            self.constants.UI_MARGIN,
            screen_height - self.constants.UI_MARGIN_BOTTOM,
            self.constants.UI_HEALTH_WIDTH,
            self.constants.UI_HEALTH_HEIGHT
        )
        
        # Rectángulo jugador 2 (derecha)
        self.background_rect_p2 = pygame.Rect(
            screen_width - self.constants.UI_HEALTH_WIDTH - self.constants.UI_MARGIN,
            screen_height - self.constants.UI_MARGIN_BOTTOM,
            self.constants.UI_HEALTH_WIDTH,
            self.constants.UI_HEALTH_HEIGHT
        )

    def dibujar(self, pantalla=Pantalla, jugadores=None):
        if not jugadores or len(jugadores) < 2:
            return
            
        display = pantalla.get_screen_data("display")
        
        # Dibujar barra de vida jugador 1
        self._draw_player_health_bar(
            display, 
            jugadores[0].get_health_percentage(),
            self.background_rect_p1
        )
        
        # Dibujar barra de vida jugador 2
        self._draw_player_health_bar(
            display,
            jugadores[1].get_health_percentage(),
            self.background_rect_p2
        )

    def _draw_player_health_bar(self, display, health_percentage, background_rect):
        """Draw health bar for a specific player"""
        # Fondo
        pygame.draw.rect(display, self.colors['background'], background_rect)
        
        # Barra de vida actual
        health_rect = background_rect.copy()
        health_rect.width = self.constants.UI_HEALTH_WIDTH * health_percentage
        pygame.draw.rect(display, self.colors['health'], health_rect)
        
        # Borde
        pygame.draw.rect(display, self.colors['border'], background_rect, 2)

class PlayerControls:
    """Configuration class for player controls"""
    def __init__(self, up=pygame.K_UP, down=pygame.K_DOWN, 
                 left=pygame.K_LEFT, right=pygame.K_RIGHT):
        self.controls = {
            'up': up,
            'down': down,
            'left': left,
            'right': right
        }
    
    def get_key(self, action):
        return self.controls.get(action)
    
    def set_key(self, action, key):
        if action in self.controls:
            self.controls[action] = key

    @classmethod
    def get_default_controls(cls, player_number=1):
        if player_number == 1:
            return cls(pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT)
        return cls(pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d)

# Modificar la función main para usar GameStateManager
def main():
    pygame.init()
    pygame.mixer.init()  # Inicializar el sistema de sonido
    
    pantalla_principal = Pantalla(800, 600, "Ultimate Cube Battle")
    tamaño_baldosa = pantalla_principal.get_screen_data("tile_size")
    controlador = controlador_plataformas()
    
    # Crear jugadores
    mid_x = pantalla_principal.get_screen_data("mid_x")
    jugadores = [
        Personaje(
            mid_x - 50,  # Más a la izquierda
            300,
            tamaño_baldosa,
            player_id=1
        ),
        Personaje(
            mid_x + 50,  # Más a la derecha
            300,
            tamaño_baldosa,
            player_id=2
        )
    ]
    
    hud = HUD(GameConstants)

    try:
        game_manager = GameStateManager(
            pantalla_principal,
            jugadores,
            controlador,
            hud
        )
        game_manager.run()
    except KeyboardInterrupt:
        print("Interrupción del teclado detectada. Saliendo del juego...")
    finally:
        pantalla_principal.detener()
        pygame.quit()

if __name__ == "__main__":
    main()

