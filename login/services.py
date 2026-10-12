import requests
def consultar_cep(cep):
    cep = "".join(
        c for c in cep
        if c.isdigit()
    )
    if len(cep) != 8:
        return None
    try:
        response = requests.get(f"https://viacep.com.br/ws/{cep}/json/",timeout=5)
        response.raise_for_status()
        data = response.json()
        if data.get("erro"):
            return None
        return data
    except requests.RequestException:
        return None