from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
import urllib3
import re

urllib3.disable_warnings()
app = FastAPI()

URL = "https://ingresosjudiciales.csj.gov.py"
PATH = "/LiquidacionesWeb/cotizacionesActualesParticulares.seam"
HDR = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def fetch_html():
    s = requests.Session()
    s.verify = False
    r = s.get(URL + PATH, headers=HDR, timeout=15)
    return r

@app.get("/")
def root():
    return {"status": "ok", "info": "API Cotizacion USD - CSJ Paraguay"}

@app.get("/debug")
def debug():
    try:
        r = fetch_html()
        return {
            "status_code": r.status_code,
            "url_final": r.url,
            "html": r.text[:5000]
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/usd")
def get_usd():
    try:
        r = fetch_html()
        soup = BeautifulSoup(r.text, "html.parser")
        compra = "0"
        venta = "0"
        encontrado = False
        for row in soup.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) >= 3:
                txt = cells[0].get_text(strip=True).upper()
                if "DOLAR" in txt or "USD" in txt:
                    compra = cells[1].get_text(strip=True)
                    venta = cells[2].get_text(strip=True)
                    encontrado = True
                    break
        if not encontrado:
            texto = r.text.upper()
            pos = texto.find("DOLAR")
            if pos > 0:
                frag = r.text[pos:pos+300]
                nums = re.findall(r'[\d]{1,2}\.[\d]{3}', frag)
                if len(nums) >= 1:
                    compra = nums[0]
                if len(nums) >= 2:
                    venta = nums[1]
                encontrado = True
        return {
            "status": "ok",
            "moneda": "USD",
            "compra": compra,
            "venta": venta,
            "encontrado": encontrado
        }
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}
