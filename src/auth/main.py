from ast import Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


class ItemIn(BaseModel):
    name : str
    price : float
    in_stock : bool = True

class Item(ItemIn):
    id : int

items : Dict[int, Item] = {}

@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return items[item_id]