from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

# 1. Obtenemos la ruta absoluta del archivo actual (main.py)
BASE_DIR = Path(__file__).resolve().parent

# Si main.py está en src/fastapi_blog/main.py, subimos 3 niveles para llegar a fastapi_blog/
TEMPLATES_DIR = BASE_DIR.parent.parent / "templates"

app = FastAPI()

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
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
@app.get("/", include_in_schema=False) #decorator para definir un endpoint, en este caso la ruta raiz "/" y especificamos que la respuesta sera en formato HTML
@app.get("/posts") #decorator para definir un endpoint, en este caso la ruta "/posts" retornara la misma respuesta que home
#Creamos un endpoint para esta url
def home(request: Request):
    #return {"message": "Welcome to the FastAPI Blog!"}  -- Respuesta en formato JSON
    return templates.TemplateResponse(request, "home.html", {"posts": posts, "title": "Home"}) #Retornamos la plantilla HTML home.html y pasamos el objeto request al contexto de la plantilla


@app.get("/api/posts")
#Creamos un endpoint para esta url y retornamos la lista de posts
def get_posts():
    return posts

""" ARRIBA VEMOS LA DEFINICION DE LA API Y DOS ENDPOINTS """

