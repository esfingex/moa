import os
import io
import re
import asyncio
import logging
import requests
from datetime import datetime
from PIL import Image
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)

class NewsScraperService:
    def __init__(self, base_data_path="solaria_modules/papernews/data"):
        self.base_data_path = base_data_path
        self.tmp_path = os.path.join(self.base_data_path, "tmp")
        self.semaphore = asyncio.Semaphore(3)

    def _get_date_str(self):
        return datetime.now().strftime('%Y%m%d')

    def _link_validate(self, image_url: str):
        if image_url:
            match = re.search(r"[a-z0-9]{6}(.jpg)", image_url)
            if match is not None:
                return image_url
        return False

    async def _download_image(self, url: str, save_path: str):
        async with self.semaphore:
            try:
                # Usamos asyncio.to_thread para llamadas bloqueantes como requests
                response = await asyncio.to_thread(requests.get, url, timeout=10)
                if response.status_code == 200:
                    bimage = io.BytesIO(response.content)
                    image = Image.open(bimage)
                    if url.endswith('.webp'):
                        image.save(save_path, "webp", optimize=True, quality=100)
                    else:
                        image.save(save_path, "jpeg")
                    return save_path
            except Exception as e:
                logger.error(f"Failed to download image {url}: {e}")
        return None

    async def scrape_news(self, newspaper_id: str, weblink: str) -> str:
        """
        Descarga las imágenes del periódico, genera el PDF y retorna la ruta final.
        """
        date_str = self._get_date_str()
        
        # Directorios
        newspaper_tmp_dir = os.path.join(self.tmp_path, newspaper_id, date_str)
        newspaper_final_dir = os.path.join(self.base_data_path, newspaper_id, date_str)
        
        os.makedirs(newspaper_tmp_dir, exist_ok=True)
        os.makedirs(newspaper_final_dir, exist_ok=True)
        
        pdf_filename = f"{newspaper_id}_{date_str}.pdf"
        pdf_filepath = os.path.join(newspaper_final_dir, pdf_filename)
        
        images_downloaded = []

        async with async_playwright() as p:
            # Usando el ejecutable especificado en el script original
            browser = await p.chromium.launch(executable_path="/usr/bin/google-chrome-stable", headless=True)
            page = await browser.new_page()
            
            try:
                await page.goto(weblink, timeout=60000)
                
                # Extraer links de imágenes
                all_images = await page.query_selector_all('img')
                image_urls = []
                for img in all_images:
                    src = await img.get_attribute("src")
                    if self._link_validate(src):
                        image_urls.append(src)
                    
                    data_src = await img.get_attribute("data-src")
                    if self._link_validate(data_src):
                        image_urls.append(data_src)
                
                # Desduplicar URLs
                image_urls = list(set(image_urls))
                
                # Descargar todas concurrentemente limitadas por el semáforo
                tasks = []
                for idx, url in enumerate(image_urls):
                    save_path = os.path.join(newspaper_tmp_dir, f"page_{idx:03d}.jpg")
                    tasks.append(self._download_image(url, save_path))
                
                results = await asyncio.gather(*tasks)
                images_downloaded = [path for path in results if path is not None]
                
            except Exception as e:
                logger.error(f"Playwright error during scraping {weblink}: {e}")
            finally:
                await browser.close()
                
        if not images_downloaded:
            raise Exception("No se encontraron imágenes para generar el PDF.")
            
        # Compilar imágenes a PDF
        images_downloaded.sort()
        pil_images = []
        for img_path in images_downloaded:
            try:
                img = Image.open(img_path)
                pil_images.append(img.convert('RGB'))
            except Exception as e:
                logger.error(f"Error procesando imagen {img_path}: {e}")
                
        if pil_images:
            # Guardar el PDF agrupando las imágenes
            pil_images[0].save(pdf_filepath, save_all=True, append_images=pil_images[1:])
            logger.info(f"PDF generado correctamente en {pdf_filepath}")
            return pdf_filepath
        else:
            raise Exception("No se pudo compilar el PDF a partir de las imágenes.")