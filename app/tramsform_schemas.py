from pydantic import BaseModel, Field

# ------------------- Transform Models -------------------

class TransformCircleModel(BaseModel):
    """
    Параметри для круглої трансформації зображення.
    """
    use_filter: bool = False
    height: int = Field(ge=0, default=400, description="Висота кола в пікселях")
    width: int = Field(ge=0, default=400, description="Ширина кола в пікселях")


class TransformEffectModel(BaseModel):
    """
    Параметри для застосування ефектів до зображення.
    """
    use_filter: bool = False
    art_audrey: bool = False
    art_zorro: bool = False
    cartoonify: bool = False
    blur: bool = False


class TransformResizeModel(BaseModel):
    """
    Параметри для зміни розмірів зображення.
    """
    use_filter: bool = False
    crop: bool = False
    fill: bool = False
    height: int = Field(ge=0, default=400, description="Нова висота зображення")
    width: int = Field(ge=0, default=400, description="Нова ширина зображення")


class TransformTextModel(BaseModel):
    """
    Параметри для додавання тексту на зображення.
    """
    use_filter: bool = False
    font_size: int = Field(ge=0, default=70, description="Розмір шрифту для тексту")
    text: str = Field(max_length=100, default="", description="Текст, який буде додано на зображення")


class TransformRotateModel(BaseModel):
    """
    Параметри для обертання зображення.
    """
    use_filter: bool = False
    width: int = Field(ge=0, default=400, description="Ширина зображення перед обертанням")
    degree: int = Field(ge=-360, le=360, default=45, description="Кут обертання зображення в градусах")


class TransformBodyModel(BaseModel):
    """
    Основна модель для трансформацій зображення.
    Включає всі можливі види трансформацій: коло, ефекти, зміна розмірів, текст, обертання.
    """
    circle: TransformCircleModel
    effect: TransformEffectModel
    resize: TransformResizeModel
    text: TransformTextModel
    rotate: TransformRotateModel
