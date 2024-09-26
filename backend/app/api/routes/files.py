import uuid
from typing import Any
import requests
import os

import urllib.parse
import json
from pyproj import Proj, Transformer

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

import ezdxf
from app.api.deps import CurrentUser, SessionDep
from app.models import *

router = APIRouter()


@router.get("/", response_model=Any)
def read_items(
    session: SessionDep, 
    current_user: CurrentUser
) -> Any:
    
    print(os.getcwd())
    directory_content = os.listdir(os.getcwd())
    print(directory_content)
    
    # filename = "/app"
    # if os.path.exists(filename):
    #     print("El archivo existe.")
    #     doc = ezdxf.readfile(filename)
    # else:
    #     print(f"El archivo {filename} no se encuentra.")
    # print(os.getcwd())
    # filename = 'bn-55.dxf'
    doc = ezdxf.readfile('/app/app/api/files/bn-55.dxf')

    print("doc", doc)