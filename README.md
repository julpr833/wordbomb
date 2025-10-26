<div align="center">
    <img width="150" height="150" src="https://i.imgur.com/bkOWbtZ.png" alt="Logo WordBomb">
    <h1>WordBomb - Backend</h1>
</div>

## Tabla de Contenidos
- [Descripción](#descripción)
- [Características](#características)
- [Modos de Juego](#modos-de-juego)
- [Dificultades](#dificultades)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Instalación](#instalación)
- [Despliegue](#despliegue)
- [API](#endpoints-de-la-api)
- [WebSockets](#eventos-websocket)
- [Licencia](#licencia)

## Descripción

WordBomb es un juego multijugador en tiempo real donde los jugadores compiten para escribir palabras que cumplan con ciertos requisitos antes de que se acabe el tiempo. Inspirado en jklm.fun, este proyecto fue desarrollado como trabajo integrador final para las materias de Estructura de Datos, Programación y Práctica Profesional Laboratorio en el Instituto Superior Adventista de Misiones.

## Características

- Tiempo real con WebSockets para una experiencia de juego fluida
- Múltiples modos de juego con diferentes mecánicas
- Sistema de puntuación basado en longitud de palabras, velocidad y dificultad
- Autenticación segura con JWT
- Almacenamiento persistente en base de datos MySQL
- API RESTful para operaciones asíncronas
- Sistema de salas para partidas privadas
- Chat en tiempo real integrado

## Modos de Juego

### 1. CLASSIC (Clásico)
- Los jugadores reciben una secuencia de letras (ej: "BO")
- Deben escribir una palabra que **contenga** esas letras en ese orden
- Ejemplo: Para "BO" → "BOMBA", "ROBOT", "ABO" son válidas

### 2. REVERSED (Inverso)
- Los jugadores reciben letras prohibidas (ej: "AE")
- Deben escribir una palabra que **NO contenga** ninguna de esas letras
- Ejemplo: Para "AE" → "ROBOT", "MUNDO" son válidas, pero "CASA" o "PERRO" no

### 3. HARDCORE (Difícil)
- Los jugadores reciben un patrón con letras en posiciones específicas (ej: "_O_B_")
- Deben escribir una palabra que coincida exactamente con ese patrón
- Ejemplo: Para "_O_B_" → "BOMBA" (5 letras, O en pos 2, B en pos 4)

## Dificultades

### Fácil
- Tiempo por turno: 15 segundos
- Longitud del prompt: 2 letras
- Multiplicador de puntos: 1.0x

### Normal
- Tiempo por turno: 12 segundos
- Longitud del prompt: 3 letras
- Multiplicador de puntos: 1.2x

### Difícil
- Tiempo por turno: 10 segundos
- Longitud del prompt: 4 letras
- Multiplicador de puntos: 1.5x

## Estructura del Proyecto

```
wordbomb/
│
├─ src/
│   ├─ routes/           # Rutas de la API REST
│   │   ├─ api/          # Endpoints de la API
│   │   └─ game/         # Rutas del juego
│   │
│   ├─ events/           # Manejadores de eventos en tiempo real
│   │   ├─ game_events.py # Lógica del juego por WebSocket
│   │   └─ __init__.py
│   │
│   ├─ lib/              # Bibliotecas y utilidades
│   │   ├─ game_logic.py # Lógica central del juego
│   │   ├─ database.py   # Conexión a MySQL
│   │   └─ rooms.py      # Gestión de salas de juego
│   │
│   └─ middleware/       # Middlewares y decoradores
│      └─ auth.py        # Autenticación y autorización
│
├─ run.py                # Punto de entrada de la aplicación
├─ requirements.txt      # Dependencias de Python
└─ .env                  # Variables de entorno
```

## Instalación

1. Clonar el repositorio
   ```bash
   git clone https://github.com/tuusuario/wordbomb-backend.git
   cd wordbomb-backend
   ```

2. Configurar entorno virtual
   ```bash
   python -m venv venv
   # En Windows:
   venv\Scripts\activate
   # En Linux/Mac:
   source venv/bin/activate
   ```

3. Instalar dependencias
   ```bash
   pip install -r requirements.txt
   ```

4. Configurar variables de entorno
   ```bash
   cp .env.example .env
   # Editar .env con tus credenciales
   ```

5. Iniciar el servidor
   ```bash
   python run.py
   ```

## Despliegue

### Requisitos
- Python 3.8+
- MySQL 8.0+
- Redis (opcional, recomendado para producción)

### Variables de entorno necesarias
```
FLASK_APP=run.py
FLASK_ENV=development  # Cambiar a 'production' en producción
SECRET_KEY=tu_clave_secreta_aqui
MYSQL_HOST=localhost
MYSQL_USER=usuario
MYSQL_PASSWORD=contraseña
MYSQL_DB=wordbomb
JWT_SECRET_KEY=otra_clave_secreta
```

## Endpoints de la API

### Autenticación
- `POST /api/auth/register` - Registrar nuevo usuario
- `POST /api/auth/login` - Iniciar sesión
- `GET /api/auth/me` - Obtener información del usuario actual

### Juego
- `GET /api/game/rooms` - Listar salas disponibles
- `POST /api/game/rooms` - Crear nueva sala
- `GET /api/game/ranking` - Ver ranking de jugadores

## Eventos WebSocket

### Cliente → Servidor
- `join_room` - Unirse a una sala
- `start_game` - Iniciar partida
- `submit_word` - Enviar palabra
- `chat_message` - Enviar mensaje al chat

### Servidor → Cliente
- `player_joined` - Un jugador se unió
- `game_started` - El juego comenzó
- `new_turn` - Nuevo turno iniciado
- `word_accepted` - Palabra correcta
- `word_rejected` - Palabra incorrecta
- `game_over` - Fin del juego
  
---

<div align="center">
    Desarrollado por Call of Code - 2025
</div>
> **auth.py**: Decoradores

- `@auth_required()`: Protege rutas según el rol del usuario.
- `@only_guest()`: Permite acceder solo a usuarios no logueados.

Implementa verificación de JWT y roles de usuario.

> ### src/util/

- **logger.py**: Logger con colores usando colorama.
- **validator.py**: Validaciones de usuario y contraseña.

Funciones auxiliares para la lógica del juego o gestión de usuarios.

> ### run.py

- Inicializa Flask, carga rutas y blueprints.
- Configura JWT, base de datos y claves de sesión.
- Punto de entrada para levantar el servidor.

## Requisitos

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Establecer variables de entorno (`.env`)

```ini
# Puerto
PORT=7777

# Configuración de la base de datos
MYSQL_HOST=""
MYSQL_PORT=1111
MYSQL_USER=""
MYSQL_PASSWORD=""
MYSQL_DB=""

# Token secreto para JWT
SESSION_SECRET=""
```

## Uso

Iniciar el servidor

```bash
python run.py
```

## Endpoints principales

### Autenticación

- `/api/auth/login (POST)` - Inicia sesión y devuelve un JWT.
- `/api/auth/register (POST)` - Registra un nuevo usuario y le asigna el rol Usuario.

> Nota:  
> Las rutas de login y registro solo pueden usarlas usuarios no logueados (only_guest).

## Sistema de Juego en Tiempo Real (Flask-SocketIO)

### Características del Juego

-  **3 Modos de Juego**: Classic, Reversed, Hardcore
-  **3 Niveles de Dificultad**: Easy, Normal, Hard
-  **Multijugador en Tiempo Real**: Hasta 10 jugadores por sala
-  **Sistema de Vidas**: Configurable de 1 a 10 vidas
-  **Sistema de Puntos**: Basado en longitud de palabra y velocidad
-  **Timers Automáticos**: Límite de tiempo por turno (10-15 segundos)
-  **Validación de Palabras**: Diccionario integrado en base de datos

### Modos de Juego

#### 1. CLASSIC (Clásico)
Escribe palabras que contengan las letras dadas en orden consecutivo.
- **Prompt**: "BO"
- **Válido**: "BOMBA", "ROBOT", "ABO"

#### 2. REVERSED (Inverso)
Escribe palabras que NO contengan ninguna de las letras prohibidas.
- **Prompt**: "AE"
- **Válido**: "ROBOT", "MUNDO"
- **Inválido**: "CASA", "PERRO"

#### 3. HARDCORE (Difícil)
Escribe palabras que coincidan exactamente con el patrón dado.
- **Prompt**: "_O_B_"
- **Válido**: "BOMBA" (5 letras, O en posición 2, B en posición 4)

### Endpoints del Juego

#### Crear Sala
```bash
POST /game/create-room
Authorization: Bearer <jwt_token>
Content-Type: application/x-www-form-urlencoded

lives=3
max_players=4
game_mode=1  # 1=CLASSIC, 2=REVERSED, 3=HARDCORE
difficulty=2  # 1=EASY, 2=NORMAL, 3=HARD
```

#### Unirse a Sala
```bash
POST /game/join-room
Authorization: Bearer <jwt_token>
Content-Type: application/x-www-form-urlencoded

room_code=ABCDEF
```

### Eventos de SocketIO

#### Conectarse al servidor
```javascript
import io from 'socket.io-client';

const socket = io('http://localhost:7777', {
    transports: ['websocket']
});
```

#### Eventos principales

**Cliente → Servidor:**
- `join_room` - Unirse a una sala
- `leave_room` - Salir de una sala
- `start_game` - Iniciar el juego (solo creador)
- `submit_word` - Enviar una palabra
- `get_room_state` - Obtener estado actual

**Servidor → Cliente:**
- `player_joined` - Un jugador se unió
- `game_started` - El juego comenzó
- `new_turn` - Nuevo turno iniciado
- `word_accepted` - Palabra correcta
- `word_rejected` - Palabra incorrecta
- `player_timeout` - Se acabó el tiempo
- `player_eliminated` - Jugador eliminado
- `game_ended` - Juego terminado

### Cliente de Prueba

Incluye un cliente HTML de prueba en `test_client.html`:

1. Inicia el servidor: `python run.py`
2. Abre `test_client.html` en tu navegador
3. Conecta al servidor en `http://localhost:7777`
4. Ingresa nombre de usuario y código de sala
5. ¡Juega!

### Documentación Completa

Ver **[GAME_DOCUMENTATION.md](GAME_DOCUMENTATION.md)** para:
- Documentación detallada de todos los eventos
- Ejemplos de código
- Sistema de puntos
- Flujo completo del juego

## Licencia

Proyecto académico de primer año TSAS, para uso educativo.
