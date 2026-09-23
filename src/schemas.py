from pydantic import BaseModel, ConfigDict, Field

class PostBase(BaseModel): #Esta es la clase base para los modelos de Post, que define los campos comunes a todos los modelos de Post.
    title: str = Field(min_length=1, max_length=100) # aca definimos el tipo (str) y usamos Field para definir validaciones o constraints.
    content: str = Field(min_length=1)
    author: str = Field(min_length=1, max_length=50)

class PostCreate(PostBase):
    pass

class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes=True)

    id: int  # Campos agregados por el sistema. No los proporciona el usuario al crear un post, pero se incluyen en la respuesta.
    date_posted: str #solo por ahora, este campo debe ser datetime