from dataclasses import Field

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class Post(BaseModel):
    id : int
    author : str
    title : str
    content : str

class createPost(Post):
    id : int 
    author :str = Field(minlength=3, max_length=50)
    title : str = Field(minlength=3, max_length=50)
    content : str = Field(minlength=3, max_length=50)

class updatePost(Post):
    title : str = Field(minlength=3, max_length=50)
    content : str = Field(minlength=3, max_length=50)

posts_db: dict[int, Post] = {}


@app.get("/posts")
def get_posts(limit : int =10, skip : int = 0):
    return list(posts_db.values())[skip: skip + limit]
   

@app.get("/posts/{id}")
def get_post(id : int):
    for post in posts_db.values():
           if post.id == id:
               return post
    raise HTTPException(status_code=404, detail="Post not found")

@app.post("/posts")
def create_post(post_data: createPost):
    post = Post(**post_data.dict())
    posts_db[post.id] = post
    raise HTTPException(status_code=201, detail="Post created successfully")

@app.put("/posts/{id}")
def update_post(id : int, post_data: updatePost):
    if id in posts_db:
        post = posts_db[id]
        post.title = post_data.title
        post.content = post_data.content
        posts_db[id] = post
    raise HTTPException(status_code=404, detail="Post not found")


@app.delete("/posts/{id}")
def delete_post(id : int):
    if id in posts_db:
        del posts_db[id]
        raise HTTPException(status_code=201, detail=f"Post with id {id} deleted successfully")
    raise HTTPException(status_code=404, detail="Post not found")