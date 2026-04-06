from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings()
app = FastAPI()

URL = "https://ingresosjudiciales.csj.gov.py"
PATH = "/LiquidacionesWeb/cotizacionesActualesParticulares.seam"
HDR = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def obtener_tabla():
    r = requests.get(URL + PATH, verify=False, timeout=15, headers=HDR)
    soup = BeautifulSoup(r.text, "html.parser")
    tabla = soup.find("table", {"id": lambda x: x and "cotizacionesId" in x})
    monedas = []
    if tabla:
        for tr in tabla.find("tbody").find_all("tr"):
            celdas = tr.find_all("td")
            if len(celdas) == 4:
                monedas.append({
                    "codigo": celdas[0].get_text(strip=True),
                    "moneda": celdas[1].get_text(strip=True),
                    "fecha": celdas[2].get_text(strip=True),
                    "tipo_cambio": celdas[3].get_text(strip=True)
                })
    return monedas

@app.get("/")
def root():
    return {"status": "ok", "info": "API Cotizacion USD - CSJ Paraguay"}

@app.get("/usd")
def get_usd():
    try:
        monedas = obtener_tabla()
        for m in monedas:
            if m["codigo"] == "US":
                return {
                    "status": "ok",
                    "codigo": m["codigo"],
                    "moneda": m["moneda"],
                    "fecha": m["fecha"],
                    "tipo_cambio": m["tipo_cambio"],
                    "descripcion": "Guaranies por 1 USD"
                }
        return {"status": "error", "mensaje": "USD no encontrado"}
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}

@app.get("/todas")
def get_todas():
    try:
        monedas = obtener_tabla()
        return {"status": "ok", "cotizaciones": monedas}
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}
