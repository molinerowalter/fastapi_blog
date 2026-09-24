from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse 
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException   

from sqlalchemy import select
from sqlalchemy.orm import Session

import models
from database import Base, engine, get_db #Base & engine se utilizan para crear tablas y get_db devuelve las sessions del database

from schemas import PostCreate, PostResponse, UserCreate, UserResponse

from typing import Annotated


Base.metadata.create_all(bind=engine)

from pathlib import Path

# 1. Obtenemos la ruta absoluta del archivo actual (main.py)
BASE_DIR = Path(__file__).resolve().parent

# Si main.py está en src/fastapi_blog/main.py, subimos 3 niveles para llegar a fastapi_blog/
TEMPLATES_DIR = BASE_DIR.parent.parent / "templates"

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


#------------------------------------------------------------ USERS ENDPOINTS ------------------------

@app.post("/api/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED) #decorator para definir un endpoint, en este caso la ruta "/api/posts" retornara el post creado en formato JSON y especificamos el modelo de respuesta y el codigo de estado HTTP
def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]):  #db: Annotated[Session, Depends(get_db)] --> Dice a FastAPI . Antes de llamar a esta funcion llama a get_db para traer la session actual. La crea y la limpia al finalizar la consulta.
    result = db.execute(select(models.User).where(models.User.username == user.username))
    existing_user = result.scalars().first();

    if existing_user:
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    result = db.execute(select(models.User).where(models.User.email == user.email))
    existing_email = result.scalars().first();
    
    if existing_email:
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )

    new_user = models.User(
        username=user.username,
        email=user.email
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user #Pydantic lo convertira a UserResponse

@app.get("api/users/{user_id}", response_model=UserResponse) 
def get_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.user_id == user_id))
    user = result.scalars().first()

    if user: 
        return user

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
    )


@app.get("/api/users/{user_id}/posts", response_model=list[PostResponse])
def get_user_posts(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    result = db.execute(select(models.Post).where(models.Post.user_id == user_id))
    posts = result.scalars().all()
    return posts


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

@app.get("/users/{user_id}/posts", include_in_schema=False, name="user_posts")
def user_posts_page(
    request: Request,
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    result = db.execute(select(models.Post).where(models.Post.user_id == user_id))
    posts = result.scalars().all()
    return templates.TemplateResponse(
        request,
        "user_posts.html",
        {"posts": posts, "user": user, "title": f"{user.username}'s Posts"},
    )


#------------------------------------------------------------ POSTS ENDPOINTS ------------------------

@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
def home(request: Request, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Post))
    posts = result.scalars().all()
    return templates.TemplateResponse(
        request,
        "home.html",
        {"posts": posts, "title": "Home"},
    )
@app.get("/api/posts", response_model=list[PostResponse]) #decorator para definir un endpoint, en este caso la ruta "/api/posts" retornara la lista de posts en formato JSON y especificamos el modelo de respuesta y el codigo de estado HTTP
#Creamos un endpoint para esta url y retornamos la lista de posts
def get_posts(db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Post))
    posts = result.scalars().all()

    return posts

@app.post(
    "/api/posts",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_post(post: PostCreate, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.id == post.user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    new_post = models.Post(
        title=post.title,
        content=post.content,
        user_id=post.user_id,
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post
    

@app.get("/posts/{post_id}", include_in_schema=False)
def post_page(request: Request, post_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if post:
        title = post.title[:50]
        return templates.TemplateResponse(
            request,
            "post.html",
            {"post": post, "title": title},
        )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

@app.get("/api/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if post:
        return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

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