from app.core.database import Base
from app.core.database.fields import Char, Text, DateTime, Boolean, Selection

class News(Base):
    """
    Paper News Model.
    """
    _name = "papernews.news"
    _description = "Press News Article"

    title = Char(string="Title", required=True, tracking=True)
    content = Text(string="Original Content")
    summary = Text(string="AI Summary")
    source = Char(string="Source / URL")
    date = DateTime(string="Publication Date")
    
    active = Boolean(string="Active", default=True)

    # Nuevos campos
    pdf_path = Char(string="PDF Path", required=False)
    state = Selection(
        string="State",
        options=[
            ("draft", "Draft"),
            ("pending", "Pending"),
            ("downloaded", "Downloaded"),
            ("error", "Error")
        ],
        default="draft"
    )

    @classmethod
    async def run_scraper_cron(cls):
        """
        Ejecuta el servicio de web scraping para los diarios.
        """
        import logging
        from .services.news_scraper import NewsScraperService
        logger = logging.getLogger(__name__)
        logger.info("Iniciando Cron de Scraping de Periódicos...")
        
        service = NewsScraperService()
        
        # Ejemplo: Ejecutar scraper para El Mercurio de Antofagasta
        try:
            pdf_path = await service.scrape_news("mercurioantofagasta", "https://www.mercurioantofagasta.cl/")
            # Crear el registro en BD
            await cls.create({
                "title": f"El Mercurio de Antofagasta - {service._get_date_str()}",
                "source": "https://www.mercurioantofagasta.cl/",
                "pdf_path": pdf_path,
                "state": "downloaded"
            })
            logger.info("Cron de Scraping finalizado con éxito.")
        except Exception as e:
            logger.error(f"Error en Cron de Scraping: {e}")

    @classmethod
    async def run_mailing_cron(cls):
        """
        Ejecuta el servicio de mailing para enviar los periódicos descargados.
        """
        import logging
        from .services.email_sender import EmailSenderService
        logger = logging.getLogger(__name__)
        logger.info("Iniciando Cron de Mailing de Periódicos...")
        
        service = EmailSenderService()
        await service.send_newspaper("mercurioantofagasta", "/path/to/pdf")
        logger.info("Cron de Mailing finalizado.")