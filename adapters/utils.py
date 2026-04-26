import sqlite3
from pathlib import Path

def get_cavemem_context(query: str, skill: str | None = None, limit: int = 5) -> str:
    """
    Extrae contexto comprimido de la DB local de cavemem (SQLite).
    Permite que MOA tenga memoria persistente de lo que ha hecho.
    """
    db_path = Path.home() / ".cavemem" / "data.db"
    if not db_path.exists():
        return ""
    
    try:
        conn = sqlite3.connect(str(db_path))
        conn.execute("PRAGMA journal_mode=WAL;") 
        cursor = conn.cursor()
        
        sql = """
            SELECT observation FROM observations 
            WHERE (observation LIKE ? OR observation LIKE ?)
            ORDER BY timestamp DESC LIMIT ?
        """
        params = [f'%{query[:20]}%', f'%{skill}%' if skill else '%%', limit]
        
        cursor.execute(sql, tuple(params))
        rows = cursor.fetchall()
        conn.close()
        
        if rows:
            header = f"\n\n## MEMORIA MOA ({skill.upper() if skill else 'GLOBAL'})\n"
            return header + "\n".join([r[0] for r in rows])
    except Exception:
        pass
    return ""
