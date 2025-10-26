# 🚀 Quick Start - Word Bomb

## Inicio Rápido en 5 Minutos

### 1. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar .env
Asegúrate de tener tu archivo `.env` configurado con la base de datos.

### 3. Iniciar Servidor
```bash
python run.py
```

### 4. Probar el Juego

#### Opción A: Cliente HTML de Prueba
1. Abre `test_client.html` en tu navegador
2. Conecta a `http://localhost:7777`
3. Ingresa un nombre de usuario
4. Crea o únete a una sala

#### Opción B: Usando cURL y JavaScript

**Paso 1: Registrarse/Login (obtener JWT)**
```bash
curl -X POST http://localhost:7777/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpass"
```

**Paso 2: Crear una sala**
```bash
curl -X POST http://localhost:7777/game/create-room \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "lives=3&max_players=4&game_mode=1&difficulty=2"
```

**Paso 3: Conectar con SocketIO (JavaScript)**
```javascript
const socket = io('http://localhost:7777');

socket.on('connect', () => {
    console.log('Conectado!');
    
    // Unirse a sala
    socket.emit('join_room', {
        room_code: 'ABCDEF',
        username: 'testuser'
    });
});

// Escuchar eventos
socket.on('game_started', (data) => {
    console.log('Juego iniciado!', data);
});

socket.on('new_turn', (data) => {
    console.log('Turno de:', data.player);
    console.log('Prompt:', data.prompt);
    
    // Enviar palabra
    socket.emit('submit_word', {
        room_code: 'ABCDEF',
        username: 'testuser',
        word: 'BOMBA'
    });
});
```

## 🎮 Flujo Típico de Juego

```
1. Usuario A crea sala → Recibe código (ej: "ABCDEF")
2. Usuario A y B se conectan vía WebSocket
3. Usuario A y B hacen join_room con el código
4. Usuario A (creador) emite start_game
5. Servidor genera prompt y emite new_turn
6. Jugador actual envía submit_word
7. Servidor valida y emite word_accepted o word_rejected
8. Servidor avanza al siguiente turno
9. Repetir hasta que quede 1 jugador
10. Servidor emite game_ended con ganador
```

## 📝 Ejemplo Completo de Partida

### Jugador 1 (Creador)
```javascript
// 1. Crear sala (HTTP)
fetch('http://localhost:7777/game/create-room', {
    method: 'POST',
    headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: 'lives=3&max_players=4&game_mode=1&difficulty=2'
})
.then(res => res.json())
.then(data => {
    const roomCode = data.room_code; // "ABCDEF"
    
    // 2. Conectar WebSocket
    const socket = io('http://localhost:7777');
    
    socket.on('connect', () => {
        // 3. Unirse a la sala
        socket.emit('join_room', {
            room_code: roomCode,
            username: 'Player1'
        });
    });
    
    // 4. Esperar a que otros jugadores se unan
    socket.on('player_joined', (data) => {
        console.log('Jugadores:', data.players);
        
        // 5. Cuando estén listos, iniciar juego
        if (data.players.length >= 2) {
            socket.emit('start_game', {
                room_code: roomCode,
                username: 'Player1'
            });
        }
    });
    
    // 6. Jugar
    socket.on('new_turn', (data) => {
        if (data.player === 'Player1') {
            // Es mi turno
            console.log('Mi turno! Prompt:', data.prompt.prompt);
            
            // Enviar palabra
            setTimeout(() => {
                socket.emit('submit_word', {
                    room_code: roomCode,
                    username: 'Player1',
                    word: 'BOMBA'
                });
            }, 2000);
        }
    });
    
    socket.on('word_accepted', (data) => {
        console.log(`✅ ${data.username}: ${data.word} (+${data.points})`);
    });
    
    socket.on('game_ended', (data) => {
        console.log('🏆 Ganador:', data.winner);
        console.log('Puntuaciones finales:', data.final_scores);
    });
});
```

### Jugador 2
```javascript
// 1. Unirse a sala existente (HTTP)
fetch('http://localhost:7777/game/join-room', {
    method: 'POST',
    headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: 'room_code=ABCDEF'
})
.then(res => res.json())
.then(data => {
    // 2. Conectar WebSocket
    const socket = io('http://localhost:7777');
    
    socket.on('connect', () => {
        // 3. Unirse a la sala
        socket.emit('join_room', {
            room_code: 'ABCDEF',
            username: 'Player2'
        });
    });
    
    // 4. Jugar cuando sea mi turno
    socket.on('new_turn', (data) => {
        if (data.player === 'Player2') {
            console.log('Mi turno! Prompt:', data.prompt.prompt);
            
            socket.emit('submit_word', {
                room_code: 'ABCDEF',
                username: 'Player2',
                word: 'ROBOT'
            });
        }
    });
});
```

## 🐛 Troubleshooting

### Error: "No hay conexión al servidor"
- Verifica que el servidor esté corriendo en el puerto correcto
- Revisa que FRONTEND_URL en .env esté configurado correctamente

### Error: "Sala no encontrada"
- El código de sala es case-sensitive (mayúsculas)
- Las salas se eliminan cuando el juego termina

### Error: "La palabra no existe en el diccionario"
- Asegúrate de tener palabras en la tabla PALABRA de la base de datos
- La palabra debe estar en mayúsculas

### Error: "No es tu turno"
- Solo el jugador actual puede enviar palabras
- Espera a que sea tu turno (evento new_turn)

## 📚 Recursos Adicionales

- **[GAME_DOCUMENTATION.md](GAME_DOCUMENTATION.md)** - Documentación completa
- **[README.md](README.md)** - Información del proyecto
- **test_client.html** - Cliente de prueba funcional

## 💡 Tips

1. **Usa el cliente de prueba** para entender el flujo antes de implementar tu frontend
2. **Revisa la consola del servidor** para ver logs de eventos en tiempo real
3. **Prueba con múltiples pestañas** del navegador para simular varios jugadores
4. **Los timers son automáticos** - no necesitas implementarlos en el cliente
5. **Las palabras deben estar en mayúsculas** para la validación

¡Listo para jugar! 🎉
