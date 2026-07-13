from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from .models import AttemptStatus, BlockKind, QuestionType, SlideType, UserRole


class LoginRequest(BaseModel):
    # намеренно str, а не EmailStr: при входе достаточно поиска по строке,
    # строгая валидация нужна только при создании пользователя
    email: str
    password: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=6)
    role: UserRole = UserRole.COORDINATOR


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    password: str | None = Field(default=None, min_length=6)
    role: UserRole | None = None
    is_active: bool | None = None


# ---------- Блоки и слайды ----------


class SlideIn(BaseModel):
    type: SlideType
    content: str = ""
    media_url: str | None = None

    @model_validator(mode="after")
    def check_media(self):
        if self.type in (SlideType.IMAGE, SlideType.VIDEO) and not self.media_url:
            raise ValueError("Для слайда с картинкой/видео нужен media_url")
        return self


class SlideOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    position: int
    type: SlideType
    content: str
    media_url: str | None


class BlockCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = ""
    kind: BlockKind = BlockKind.ELECTIVE


class BlockUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    kind: BlockKind | None = None
    position: int | None = None
    is_published: bool | None = None


class ProgressOut(BaseModel):
    last_slide: int = 0
    viewed: bool = False
    # статус лучшей попытки теста: passed / pending_review / failed / None
    test_status: AttemptStatus | None = None


class BlockListItem(BaseModel):
    id: int
    title: str
    description: str
    kind: BlockKind
    position: int
    is_published: bool
    slide_count: int
    has_test: bool
    progress: ProgressOut


class BlockDetail(BlockListItem):
    slides: list[SlideOut]


class ProgressIn(BaseModel):
    last_slide: int = Field(ge=0)


# ---------- Тесты: редактирование ----------


class OptionIn(BaseModel):
    text: str = Field(min_length=1)
    is_correct: bool = False


class QuestionIn(BaseModel):
    text: str = Field(min_length=1)
    type: QuestionType
    options: list[OptionIn] = []

    @model_validator(mode="after")
    def check_options(self):
        if self.type == QuestionType.OPEN:
            self.options = []
            return self
        if len(self.options) < 2:
            raise ValueError("Вопросу с вариантами нужно минимум 2 варианта")
        correct = sum(1 for o in self.options if o.is_correct)
        if correct == 0:
            raise ValueError("Отметьте хотя бы один верный вариант")
        if self.type == QuestionType.SINGLE and correct > 1:
            raise ValueError("У вопроса с одним ответом верный вариант должен быть один")
        return self


class TestIn(BaseModel):
    pass_threshold: int = Field(default=70, ge=1, le=100)
    questions: list[QuestionIn] = Field(min_length=1)


class OptionEditOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
    is_correct: bool


class QuestionEditOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
    type: QuestionType
    options: list[OptionEditOut]


class TestEditOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    pass_threshold: int
    questions: list[QuestionEditOut]


# ---------- Тесты: прохождение ----------


class OptionPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str


class QuestionPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
    type: QuestionType
    options: list[OptionPublic]


class TestPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    pass_threshold: int
    questions: list[QuestionPublic]


class AnswerIn(BaseModel):
    question_id: int
    option_ids: list[int] = []
    text: str = ""


class AttemptIn(BaseModel):
    answers: list[AnswerIn]


class AttemptOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: AttemptStatus
    correct_count: int
    total_count: int
    score: int | None
    created_at: datetime


# ---------- Проверка открытых ответов ----------


class OpenAnswerOut(BaseModel):
    answer_id: int
    question_text: str
    text_answer: str


class PendingAttemptOut(BaseModel):
    id: int
    user_name: str
    user_email: str
    block_title: str
    created_at: datetime
    auto_correct: int  # уже засчитано автопроверкой
    total_count: int
    open_answers: list[OpenAnswerOut]


class ReviewAnswerIn(BaseModel):
    answer_id: int
    is_correct: bool


class ReviewIn(BaseModel):
    answers: list[ReviewAnswerIn] = Field(min_length=1)


# ---------- Результаты (для обучающих координаторов) ----------


class BlockResult(BaseModel):
    block_id: int
    title: str
    kind: BlockKind
    percent: int
    viewed: bool
    test_status: AttemptStatus | None = None


class CoordinatorResult(BaseModel):
    user_id: int
    full_name: str
    email: str
    is_active: bool
    blocks_done: int
    slides_viewed: int
    tests_passed: int
    overall_percent: int
    per_block: list[BlockResult]


class ResultsBlockRef(BaseModel):
    id: int
    title: str
    kind: BlockKind


class ResultsOut(BaseModel):
    blocks: list[ResultsBlockRef]
    coordinators: list[CoordinatorResult]


class MediaUploadOut(BaseModel):
    url: str
