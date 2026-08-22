from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


class ItemIn(BaseModel):
    name : str
    price : float
    in_stock : bool = True

class Item(ItemIn):
    id : int