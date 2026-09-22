from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory="templates")
posts: list[dict]=[
    {
        "id": 1,
        "author":  "Corey Schafer",
        "title": "FastAPI YEAAH!",
        "content": "Testing FastAPI framework",
        "date_posted": "April 20, 2025",
    },
    {
        "id": 2,
        "author": "Jane Doe",
        "title": "Python is great",
        "content": "Python potencied by fastAPI",
        "date_posted": "April 21, 2025",
    }
]
# include_in_schema=False hide the route in localhost:8000/docs, so it will not appear in the documentation
@app.get("/", response_class=HTMLResponse, include_in_schema=False) #decorator para definir un endpoint, en este caso la ruta raiz "/" y especificamos que la respuesta sera en formato HTML
@app.get("/posts") #decorator para definir un endpoint, en este caso la ruta "/posts" retornara la misma respuesta que home
#Creamos un endpoint para esta url
def home():
    #return {"message": "Welcome to the FastAPI Blog!"}  -- Respuesta en formato JSON
    return f"<h1>{posts[0]['title']}</h1>" #--- Respuesta en formato HTML, retornando el titulo del primer post


@app.get("/api/posts")
#Creamos un endpoint para esta url y retornamos la lista de posts
def get_posts():
    return posts

""" ARRIBA VEMOS LA DEFINICION DE LA API Y DOS ENDPOINTS """

