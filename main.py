from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings()
app = FastAPI()

URL = "https://ingresosjudiciales.csj.gov.py"
PATH = "/LiquidacionesWeb/cotizacionesActualesParticulares.seam"
HDR = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

@app.get("/")
def root():
    return {"status": "ok", "info": "API Cotizacion USD - CSJ Paraguay"}

@app.get("/debug")
def debug():
    try:
        r = requests.get(URL + PATH, verify=False, timeout=15, headers=HDR)
        return {"status_code": r.status_code, "html": r.text[:5000]}
    except Exception as e:
        return {"error": str(e)}

@app.get("/usd")
def get_usd():
    try:
        r = requests.get(URL + PATH, verify=False, timeout=15, headers=HDR)
        soup = BeautifulSoup(r.text, "html.parser")
        valor = "0"
        fecha = ""
        for row in soup.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) >= 4:
                moneda = cells[0].get_text(strip=True).upper()
                desc = cells[1].get_text(strip=True).upper()
                if "US" in moneda or "DOLAR" in desc or "OLAR" in desc:
                    fecha = cells[2].get_text(strip=True)
                    valor = cells[3].get_text(strip=True)
                    break
        return {
            "status": "ok",
            "moneda": "USD",
            "valor": valor,
            "fecha": fecha,
            "descripcion": "Guaranies por 1 USD"
        }
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}
