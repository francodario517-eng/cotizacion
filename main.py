from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings()
app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok", "info": "API Cotizacion USD - CSJ Paraguay"}

@app.get("/usd")
def get_usd():
    url = "https://ingresosjudiciales.csj.gov.py"
    path = "/LiquidacionesWeb/cotizacionesActualesParticulares.seam"
    try:
        r = requests.get(
            url + path,
            verify=False,
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        soup = BeautifulSoup(r.text, "html.parser")
        compra = "0"
        venta = "0"
        for row in soup.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) >= 3:
                txt = cells[0].get_text(strip=True).upper()
                if "DOLAR" in txt:
                    compra = cells[1].get_text(strip=True)
                    venta = cells[2].get_text(strip=True)
                    break
        return {
            "status": "ok",
            "moneda": "USD",
            "compra": compra,
            "venta": venta
        }
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}
