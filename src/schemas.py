from datetime import datetime;

from pydantic import BaseModel, ConfigDict, Field, EmailStr

#Tenemos definidos 3 layers o niveles. --> Request --> Pydantic validation --> SQLAlchemy search and return to Pydantic --> Pydantic returns to UI

#------------------------------------------------------------- USERS --------------------------------------------------------------


class UserBase(BaseModel): #Esta es la clase base para los modelos de Post, que define los campos comunes a todos los modelos de Post.
    username: str = Field(min_length=1, max_length=50);
    email: EmailStr = Field(max_length=120) #EmailStr de Pydantic ya aplica las constraints propias de un email tipico, que no sea vacio, el @ etc...
    pass

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    model_config = ConfigDict(from_attribute=True)

    id: int
    image_file: str | None
    image_path: str

#------------------------------------------------------------- POSTS --------------------------------------------------------------

class PostBase(BaseModel): #Esta es la clase base para los modelos de Post, que define los campos comunes a todos los modelos de Post.
    title: str = Field(min_length=1, max_length=100) # aca definimos el tipo (str) y usamos Field para definir validaciones o constraints.
    content: str = Field(min_length=1)
    author: str = Field(min_length=1, max_length=50)

class PostCreate(PostBase):
    user_id: int #TEMPORARY Despues usaremos el user de la session actual

class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes=True)

    id: int  # Campos agregados por el sistema. No los proporciona el usuario al crear un post, pero se incluyen en la respuesta.
    user_id: int
    date_posted: datetime #solo por ahora, este campo debe ser datetime
    author: UserResponse