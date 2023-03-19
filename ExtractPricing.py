import json
import asyncio
from bs4 import BeautifulSoup
from lxml import etree
from datetime import datetime
from requests_html import AsyncHTMLSession

# crear una sesión HTML para interactuar con el código javascript de la página, esto se utilizará principalmente para poder ver el stock y validar cuantos precios tiene
async def ExtractPricingProduct(product):
    session = AsyncHTMLSession()
    url = f'https://www.a3d.cl/{product}'
    try:
        response = await session.get(url)
        await response.html.arender()
        soup = BeautifulSoup(response.html.html, 'html.parser')
        # Extracción de datos de producto
        dom = etree.HTML(str(soup))
        root = '//div[@class="product-info-main"]//div[@class="product-info-price"]//div[@class="price-box price-final_price"]'
        special_price_validation = dom.xpath(f'{root}//span[@class="price-wrapper"]')
        if len(special_price_validation) == 2:
            old_price = dom.xpath(f'{root}//span[@class="old-price"]//span[@class="price"]')[0].text
            old_price = int(old_price.replace("$", "").replace(".", ""))
            special_price = dom.xpath(f'{root}//span[@class="special-price"]//span[@class="price"]')[0].text
            special_price = int(special_price.replace("$", "").replace(".", ""))
        else:
            old_price = dom.xpath(f'{root}//span[@class="price"]')[0].text
            old_price = int(old_price.replace("$", "").replace(".", ""))
            special_price = 0

        # Crea un diccionario con los datos a almacenar
        data = {
            'product': product,
            'url': url,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'old_price': old_price,
            'special_price': special_price
        }
    except Exception as e:
        print(f'Error al procesar el producto {product}: {str(e)}')
        data = None
    finally:
        await session.close()

    return data

async def main():
    # Lista de productos a extraer precios
    products = ['calming-heat']
    # Lee la ruta del archivo JSON desde el archivo de configuración
    with open('config.txt', 'r') as config_file:
        json_path = config_file.read().strip()
    # Abre el archivo JSON
    with open(json_path, 'a') as f:
        for product in products:
            # Ejecuta la función asincrónicamente
            data = await ExtractPricingProduct(product)
            if data:
                # Escribe los datos en el archivo si hay información para el producto
                json.dump(data, f, default=str)
                f.write('\n') # Agrega una nueva línea para separar los datos en el archivo

asyncio.run(main())
input('Presione la tecla intro para salir...')