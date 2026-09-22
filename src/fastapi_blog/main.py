from fastapi import FastAPI, Request, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse 
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException    
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

@app.get("/posts/{post_id}", include_in_schema=False) #Si retornamo HTML no lo mostraremos en la documentacion
def get_post(request: Request, post_id: int):
    for post in posts:
        if post.get("id") == post_id:
            return templates.TemplateResponse(request, "post.html", {"post": post, "title": post["title"]})
    return templates.TemplateResponse(request, "error.html", {"status_code": status.HTTP_404_NOT_FOUND, "detail": "Post not found"})

""" ARRIBA VEMOS LA DEFINICION DE LA API Y DOS ENDPOINTS """

@app.exception_handler(StarletteHTTPException)
def general_http_exception_handler(request: Request, exc: StarletteHTTPException):
    message = (exc.detail if exc.detail else "An error occurred")

    if request.url.path.startswith("/api"):
        # Manejar excepciones HTTP para rutas que comienzan con /api
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": message},
        )
    # Manejar excepciones HTTP generales
    return templates.TemplateResponse(request, "error.html", {"status_code": exc.status_code, "title": exc.status_code, "detail": message}, status_code=exc.status_code)

@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    if request.url.path.startswith("/api"):
        # Manejar excepciones de validación para rutas que comienzan con /api
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors()},
        )
    # Manejar excepciones de validación generales
    return templates.TemplateResponse(request, "error.html", {"status_code": status.HTTP_422_UNPROCESSABLE_ENTITY, "title": "Validation Error", "detail": "Invalid request. Please check your input and try again."}, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)