import asyncio
import logging
from app.core.database import db
from solaria_modules.papernews.models.papernews import News

logging.basicConfig(level=logging.INFO)

async def test_cron():
    print("Iniciando prueba manual del Cron de Scraping...")
    # Inicializamos la base de datos (requerido para Solaria ORM)
    await db.init()
    
    # Ejecutamos el método del cron directamente
    await News.run_scraper_cron()
    
    print("Prueba finalizada. Verifica la carpeta solaria_modules/papernews/data/")

if __name__ == "__main__":
    asyncio.run(test_cron())
