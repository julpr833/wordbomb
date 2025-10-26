# Word Bomb - Documentación del Juego

## 🎮 Descripción General

Word Bomb es un juego multijugador en tiempo real inspirado en jklm.fun donde los jugadores deben escribir palabras que cumplan con ciertos requisitos antes de que se acabe el tiempo.

## 🎯 Modos de Juego

### 1. **CLASSIC (Clásico)**
- Los jugadores reciben una secuencia de letras (ej: "BO")
- Deben escribir una palabra que **contenga** esas letras en ese orden
- Ejemplo: Para "BO" → "BOMBA", "ROBOT", "ABO" son válidas

### 2. **REVERSED (Inverso)**
- Los jugadores reciben letras prohibidas (ej: "AE")
- Deben escribir una palabra que **NO contenga** ninguna de esas letras
- Ejemplo: Para "AE" → "ROBOT", "MUNDO" son válidas, pero "CASA" o "PERRO" no

### 3. **HARDCORE (Difícil)**
- Los jugadores reciben un patrón con letras en posiciones específicas (ej: "_O_B_")
- Deben escribir una palabra que coincida exactamente con ese patrón
- Ejemplo: Para "_O_B_" → "BOMBA" (5 letras, O en pos 2, B en pos 4)

## 📊 Dificultades

### EASY (Fácil)
- **Tiempo por turno:** 15 segundos
- **Longitud del prompt:** 2 letras
- **Multiplicador de puntos:** 1.0x

### NORMAL
- **Tiempo por turno:** 12 segundos
- **Longitud del prompt:** 2-3 letras
- **Multiplicador de puntos:** 1.5x

### HARD (Difícil)
- **Tiempo por turno:** 10 segundos
- **Longitud del prompt:** 3-4 letras
- **Multiplicador de puntos:** 2.0x

## 🎲 Mecánicas del Juego

### Sistema de Vidas
- Cada jugador comienza con un número configurable de vidas (1-10)
- Se pierde una vida cuando:
  - Se acaba el tiempo del turno
  - Se envía una palabra inválida
- Un jugador es eliminado cuando sus vidas llegan a 0

### Sistema de Puntos
Los puntos se calculan con la siguiente fórmula:

```
puntos_base = longitud_palabra × 10
bonus_tiempo = max(0, 50 - tiempo_respuesta × 5)
puntos_totales = (puntos_base + bonus_tiempo) × multiplicador_dificultad
```

**Factores:**
- Palabras más largas dan más puntos
- Responder más rápido da bonus (máximo 50 puntos)
- La dificultad multiplica los puntos

### Validación de Palabras
Una palabra es válida si:
1. ✅ Tiene al menos 3 letras
2. ✅ Solo contiene letras (sin números ni símbolos)
3. ✅ No ha sido usada en la partida actual
4. ✅ Existe en el diccionario del juego
5. ✅ Cumple con las reglas del modo de juego actual

### Condiciones de Victoria
El juego termina cuando:
- Solo queda 1 jugador vivo (es el ganador)
- Todos los jugadores son eliminados (gana quien tenga más puntos)

## 🔌 Eventos de SocketIO

### Eventos del Cliente → Servidor

#### `join_room`
Unirse a una sala de juego
```javascript
socket.emit('join_room', {
    room_code: 'ABCDEF',
    username: 'jugador1'
});
```

#### `leave_room`
Salir de una sala
```javascript
socket.emit('leave_room', {
    room_code: 'ABCDEF',
    username: 'jugador1'
});
```

#### `start_game`
Iniciar el juego (solo el creador)
```javascript
socket.emit('start_game', {
    room_code: 'ABCDEF',
    username: 'creador'
});
```

#### `submit_word`
Enviar una palabra durante el turno
```javascript
socket.emit('submit_word', {
    room_code: 'ABCDEF',
    username: 'jugador1',
    word: 'BOMBA'
});
```

#### `send_message`
Enviar mensaje de chat
```javascript
socket.emit('send_message', {
    room_code: 'ABCDEF',
    username: 'jugador1',
    message: 'Hola!'
});
```

#### `get_room_state`
Obtener estado actual de la sala (útil para reconexiones)
```javascript
socket.emit('get_room_state', {
    room_code: 'ABCDEF'
});
```

### Eventos del Servidor → Cliente

#### `connected`
Confirmación de conexión
```javascript
socket.on('connected', (data) => {
    console.log(data.message);
});
```

#### `player_joined`
Un jugador se unió a la sala
```javascript
socket.on('player_joined', (data) => {
    // data.username, data.players, data.room_info
});
```

#### `player_left`
Un jugador salió de la sala
```javascript
socket.on('player_left', (data) => {
    // data.username
});
```

#### `game_started`
El juego ha comenzado
```javascript
socket.on('game_started', (data) => {
    // data.players, data.gamemode, data.difficulty, data.lives
});
```

#### `new_turn`
Nuevo turno iniciado
```javascript
socket.on('new_turn', (data) => {
    // data.player (username del jugador actual)
    // data.prompt (objeto con el desafío)
    // data.time_limit (segundos)
    // data.round (número de ronda)
    // data.lives (vidas de cada jugador)
});
```

#### `word_accepted`
Palabra aceptada
```javascript
socket.on('word_accepted', (data) => {
    // data.username, data.word, data.points, data.total_points, data.time_taken
});
```

#### `word_rejected`
Palabra rechazada
```javascript
socket.on('word_rejected', (data) => {
    // data.username, data.word, data.reason, data.lives_remaining
});
```

#### `player_timeout`
Se acabó el tiempo del jugador
```javascript
socket.on('player_timeout', (data) => {
    // data.username, data.lives_remaining
});
```

#### `player_eliminated`
Un jugador fue eliminado
```javascript
socket.on('player_eliminated', (data) => {
    // data.username, data.remaining_players
});
```

#### `game_ended`
El juego terminó
```javascript
socket.on('game_ended', (data) => {
    // data.winner
    // data.final_scores (array con puntos y vidas finales)
    // data.total_rounds
    // data.total_words
});
```

#### `chat_message`
Mensaje de chat recibido
```javascript
socket.on('chat_message', (data) => {
    // data.username, data.message, data.timestamp
});
```

#### `room_state`
Estado actual de la sala
```javascript
socket.on('room_state', (data) => {
    // data.room_code, data.players, data.state
    // data.game_state (si el juego está en curso)
});
```

#### `error`
Error del servidor
```javascript
socket.on('error', (data) => {
    // data.message
});
```

## 🚀 Cómo Usar

### 1. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno
Crear archivo `.env`:
```env
SESSION_SECRET=tu_secreto_aqui
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=password
MYSQL_DB=wordbomb
FRONTEND_URL=http://localhost:3000
PORT=7777
```

### 3. Iniciar el Servidor
```bash
python run.py
```

### 4. Conectar desde el Frontend
```javascript
import io from 'socket.io-client';

const socket = io('http://localhost:7777', {
    transports: ['websocket'],
    cors: {
        origin: "http://localhost:3000"
    }
});

// Conectar
socket.on('connect', () => {
    console.log('Conectado al servidor');
});

// Unirse a una sala
socket.emit('join_room', {
    room_code: 'ABCDEF',
    username: 'MiUsuario'
});

// Escuchar eventos
socket.on('new_turn', (data) => {
    console.log(`Turno de ${data.player}`);
    console.log(`Prompt: ${data.prompt.description}`);
});
```

## 🎨 Ejemplo de Flujo de Juego

1. **Creación de Sala** (HTTP POST)
   - Usuario crea sala con configuración
   - Recibe código de sala

2. **Unirse a Sala** (HTTP POST + WebSocket)
   - Usuarios se unen con el código
   - WebSocket notifica a todos los jugadores

3. **Inicio del Juego** (WebSocket)
   - Creador inicia el juego
   - Se genera el primer prompt
   - Comienza el timer del primer turno

4. **Turnos** (WebSocket)
   - Jugador actual recibe prompt
   - Timer comienza (10-15 segundos)
   - Jugador envía palabra
   - Validación y puntos
   - Siguiente turno

5. **Eliminación** (WebSocket)
   - Jugador pierde todas sus vidas
   - Es eliminado del juego
   - Continúa con jugadores restantes

6. **Fin del Juego** (WebSocket)
   - Queda 1 jugador o todos eliminados
   - Se muestra ganador y estadísticas
   - Se guarda en base de datos

## 📝 Notas Importantes

- El servidor maneja automáticamente los timeouts de turnos
- Las palabras usadas se guardan por partida (no se pueden repetir)
- Los jugadores pueden reconectarse usando `get_room_state`
- El creador de la sala es el único que puede iniciar el juego
- Las salas se eliminan automáticamente al finalizar el juego

## 🐛 Debugging

Para ver logs del servidor:
```python
# Los eventos importantes se imprimen en consola
print(f"Cliente conectado: {request.sid}")
print(f"{username} se unió a la sala {room_code}")
print(f"Juego iniciado en sala {room_code}")
```

## 🔒 Seguridad

- Autenticación JWT requerida para crear/unirse a salas
- Validación de permisos (solo creador puede iniciar)
- Validación de turnos (solo jugador actual puede enviar palabra)
- Protección contra palabras duplicadas
- Timeouts automáticos para evitar juegos colgados
