<div align="center">
    <img width="150" height="150" src="https://i.imgur.com/bkOWbtZ.png" alt="Logo WordBomb">
</div>

# Wordbomb

Wordbomb es un juego de mecanografía inspirado en [jklm.fun](https://jklm.fun).\
Fue creado como parte del Trabajo Integrador Final de las materias `Estructura de Datos, Programación, Práctica Profesional Laboratorio` en el [Instituto Superior Adventista de Misiones](https://isam.educacionadventista.com)\
El objetivo de este proyecto es el de integrar las tecnologías aprendidas en un proyecto práctico para aplicar todos nuestros conocimientos.

Más información adjunta en el archivo `.docx`

## Estructura del proyecto

```
wordbomb/
│
├─ src/
│   ├─ routes/        # Rutas de la API (login, registro, juego, etc.)
│   ├─ database/      # Conexión y utilidades de MySQL
│   ├─ middleware/    # Decoradores y validaciones (auth, roles, JWT)
│   ├─ util/          # Funciones utilitarias (logger, validadores)
│   └─ __init__.py
│
├─ run.py             # Script principal para levantar el servidor Flask
├─ requirements.txt   # Dependencias del proyecto
├─ .env               # Variables de entorno (DB, JWT secret, etc.)
└─ README.md          # Documentación

```

## Módulos principales

> ### src/routes/
>
> Contiene las rutas del servidor, organizadas en blueprints:

- /auth: Login y registro de usuarios.
- /game: Endpoints para jugar WordBomb.

Modularización con blueprints para mantener el código limpio.

> ### src/database/
>
> **mysql.py**: Inicialización y conexión a la base de datos MySQL.

Contiene funciones para obtener cursores y manejar commits de forma segura.

> ### src/middleware/
>
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

## Licencia

Proyecto académico de primer año TSAS, para uso educativo.
