from flask import jsonify
from src.routes import api
from src.lib.database import mysql

@api.route('/users/ranking', methods=['GET'])
def get_ranking():
    """
    Obtiene el ranking de jugadores ordenado por victorias y winrate
    """
    query = """
    SELECT 
        u.Username,
        u.Avatar_URL,
        COUNT(CASE WHEN p.Ganador_ID = u.ID_Usuario THEN 1 END) AS wins,
        COUNT(pp.Partida_ID) AS total_games,
        CASE 
            WHEN COUNT(pp.Partida_ID) > 0 
            THEN (COUNT(CASE WHEN p.Ganador_ID = u.ID_Usuario THEN 1 END) * 100.0 / COUNT(pp.Partida_ID))
            ELSE 0 
        END AS winrate,
        SUM(pp.PuntosGanados) AS total_points
    FROM USUARIO u
    LEFT JOIN PARTIDA_PARTICIPANTE pp ON u.ID_Usuario = pp.Usuario_ID
    LEFT JOIN PARTIDA p ON pp.Partida_ID = p.ID_Partida
    WHERE u.Vetado = 0
    GROUP BY u.ID_Usuario, u.Username, u.Avatar_URL
    HAVING COUNT(pp.Partida_ID) > 0
    ORDER BY wins DESC, winrate DESC, total_points DESC
    LIMIT 50
    """
    
    ranking = []
    
    try:
        with mysql.get_db().cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
            
            for idx, row in enumerate(results, start=1):
                ranking.append({
                    "rank": idx,
                    "username": row[0],
                    "avatar": row[1],
                    "wins": row[2],
                    "total_games": row[3],
                    "winrate": round(row[4], 2),
                    "total_points": row[5] if row[5] else 0
                })
    except Exception as e:
        print(f"Error obteniendo ranking: {e}")
        return jsonify({"error": "Error obteniendo ranking"}), 500
    
    return jsonify(ranking)
