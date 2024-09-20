import uuid
from typing import Any
import requests
import urllib.parse
import json
from pyproj import Proj, Transformer

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import *

router = APIRouter()


@router.post("/", response_model=Any)
def read_items(
    session: SessionDep, 
    current_user: CurrentUser, 
    address: AddressPost
) -> Any:


    street_name = address.street
    street_number = address.number
    municipality = address.municipality
    provincia = address.province
    country = address.country
    address = f'{street_name} {street_number}, {municipality}, Provincia de {provincia}, {country}'
    encoded_address = urllib.parse.quote(address)

    url_base = f'https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates?SingleLine={encoded_address}&f=json&outFields=*'
    response = requests.get(url_base)

    if response.status_code == 200:
        data = response.json()
        print("*"*50)
        print("data1", data)

        if "candidates" in data and len(data["candidates"]) > 0:
            coordenates = data["candidates"][0].get("location", "No se encontró el campo 'coordenates'")
            print("coordenates", coordenates)
        else:
            raise HTTPException(
                status_code=404, 
                detail="Coordenadas no identificadas"
            )

    #COnvertir coordenadas a Webmercaotr:
    transformer = Transformer.from_crs("epsg:4326", "epsg:102100", always_xy=True)
    lat, lon = coordenates['y'], coordenates['x']
    x, y = transformer.transform(lon, lat)
    print(" X,Y>", x,y)

    url = "https://msi-gis.gestionmsi.gob.ar/server/rest/services/PARCELAS20/FeatureServer/1/query"

    geometry = {
        "x": x,
        "y": y,
        "spatialReference": {"wkid": 102100}
    }

    geometry_json = json.dumps(geometry)

    params = {
        'f': 'json',
        'returnGeometry': 'true',
        'spatialRel': 'esriSpatialRelIntersects',
        'geometryType': 'esriGeometryPoint',
        'inSR': '102100',
        'outFields': '*',
        'outSR': '102100',
        'resultType': 'tile'
    }

    encoded_params = urllib.parse.urlencode(params)
    full_url = f"{url}?{encoded_params}&geometry={urllib.parse.quote(geometry_json)}"

    response = requests.get(full_url)
    if response.status_code == 200:
        data = response.json()
        print("/"*50)
        print("data2>", data)

        data_return = {
            "address": address,
            "nomenclature": data['features'][0]['attributes']['NOMEN'],
            "circumscription": data['features'][0]['attributes']['CIR'],
            "sector": data['features'][0]['attributes']['SEC'],
            "block": data['features'][0]['attributes']['MAN'],
            "plot": data['features'][0]['attributes']['PAR'],
            "zone": data['features'][0]['attributes']['ZONA1'],
            "radius": data['features'][0]['attributes']['RADIO1'],
            "area": data['features'][0]['attributes']['Shape__Area'] * data['features'][0]['attributes']['Shape__Length'],
            "full_address": f"{address}, NOMEN: {data['features'][0]['attributes']['NOMEN']}, CIR: {data['features'][0]['attributes']['CIR']}, SEC: {data['features'][0]['attributes']['SEC']}, MAN: {data['features'][0]['attributes']['MAN']}, PAR: {data['features'][0]['attributes']['PAR']}, ZONA: {data['features'][0]['attributes']['ZONA1']}, RADIO: {data['features'][0]['attributes']['RADIO1']}"
        }

        return data_return

    else:
        raise HTTPException(
            status_code=400, 
            detail="Error encontrando el predio"
        )

   


