import enum
from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def enum_column(enum_cls, **kwargs):
    """Enum-колонка, хранящая значения (value), а не имена членов."""
    return mapped_column(
        Enum(enum_cls, values_callable=lambda e: [m.value for m in e]), **kwargs
    )


class UserRole(str, enum.Enum):
    SUPERADMIN = "superadmin"
    TRAINING_COORDINATOR = "training_coordinator"
    COORDINATOR = "coordinator"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = enum_column(UserRole, default=UserRole.COORDINATOR)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class BlockKind(str, enum.Enum):
    THEORY = "theory"  # обязательная теоретическая база
    ELECTIVE = "elective"  # блок на выбор


class SlideType(str, enum.Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"


class QuestionType(str, enum.Enum):
    SINGLE = "single"  # один верный ответ
    MULTIPLE = "multiple"  # несколько верных
    OPEN = "open"  # открытый вопрос, проверяется вручную


class AttemptStatus(str, enum.Enum):
    PENDING_REVIEW = "pending_review"
    PASSED = "passed"
    FAILED = "failed"


class Block(Base):
    __tablename__ = "blocks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")
    kind: Mapped[BlockKind] = enum_column(BlockKind, default=BlockKind.ELECTIVE)
    position: Mapped[int] = mapped_column(Integer, default=0)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)

    slides: Mapped[list["Slide"]] = relationship(
        back_populates="block",
        cascade="all, delete-orphan",
        order_by="Slide.position",
    )
    test: Mapped["Test | None"] = relationship(
        back_populates="block", cascade="all, delete-orphan", uselist=False
    )


class Slide(Base):
    __tablename__ = "slides"

    id: Mapped[int] = mapped_column(primary_key=True)
    block_id: Mapped[int] = mapped_column(ForeignKey("blocks.id"))
    position: Mapped[int] = mapped_column(Integer, default=0)
    type: Mapped[SlideType] = enum_column(SlideType, default=SlideType.TEXT)
    # content: текст слайда (для text) или подпись (для image/video)
    content: Mapped[str] = mapped_column(Text, default="")
    # media_url: /uploads/... для картинок или внешняя ссылка на видео
    media_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    # homework: текст домашнего задания к слайду; пусто — задания нет
    homework: Mapped[str] = mapped_column(Text, default="")

    block: Mapped[Block] = relationship(back_populates="slides")
    homework_checks: Mapped[list["HomeworkCheck"]] = relationship(
        back_populates="slide", cascade="all, delete-orphan"
    )
    homework_submissions: Mapped[list["HomeworkSubmission"]] = relationship(
        back_populates="slide", cascade="all, delete-orphan"
    )


class HomeworkSubmission(Base):
    """Текстовый ответ координатора на домашку слайда."""

    __tablename__ = "homework_submissions"
    __table_args__ = (UniqueConstraint("user_id", "slide_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    slide_id: Mapped[int] = mapped_column(ForeignKey("slides.id"))
    text: Mapped[str] = mapped_column(Text, default="")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utcnow, onupdate=utcnow
    )

    slide: Mapped[Slide] = relationship(back_populates="homework_submissions")
    user: Mapped[User] = relationship()


class HomeworkCheck(Base):
    """Отметка обучающего координатора: домашка слайда зачтена координатору."""

    __tablename__ = "homework_checks"
    __table_args__ = (UniqueConstraint("user_id", "slide_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    slide_id: Mapped[int] = mapped_column(ForeignKey("slides.id"))
    checked_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    checked_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    slide: Mapped[Slide] = relationship(back_populates="homework_checks")
    user: Mapped[User] = relationship(foreign_keys=[user_id])


class Test(Base):
    __tablename__ = "tests"

    id: Mapped[int] = mapped_column(primary_key=True)
    block_id: Mapped[int] = mapped_column(ForeignKey("blocks.id"), unique=True)
    pass_threshold: Mapped[int] = mapped_column(Integer, default=70)  # процент

    block: Mapped[Block] = relationship(back_populates="test")
    questions: Mapped[list["Question"]] = relationship(
        back_populates="test",
        cascade="all, delete-orphan",
        order_by="Question.position",
    )


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    test_id: Mapped[int] = mapped_column(ForeignKey("tests.id"))
    position: Mapped[int] = mapped_column(Integer, default=0)
    text: Mapped[str] = mapped_column(Text)
    type: Mapped[QuestionType] = enum_column(QuestionType, default=QuestionType.SINGLE)

    test: Mapped[Test] = relationship(back_populates="questions")
    options: Mapped[list["AnswerOption"]] = relationship(
        back_populates="question", cascade="all, delete-orphan", order_by="AnswerOption.id"
    )


class AnswerOption(Base):
    __tablename__ = "answer_options"

    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    text: Mapped[str] = mapped_column(Text)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)

    question: Mapped[Question] = relationship(back_populates="options")


class Attempt(Base):
    __tablename__ = "attempts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    test_id: Mapped[int] = mapped_column(ForeignKey("tests.id"))
    status: Mapped[AttemptStatus] = enum_column(AttemptStatus)
    correct_count: Mapped[int] = mapped_column(Integer, default=0)
    total_count: Mapped[int] = mapped_column(Integer, default=0)
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)  # процент
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    user: Mapped[User] = relationship()
    test: Mapped[Test] = relationship()
    answers: Mapped[list["Answer"]] = relationship(
        back_populates="attempt", cascade="all, delete-orphan"
    )


class Answer(Base):
    __tablename__ = "answers"

    id: Mapped[int] = mapped_column(primary_key=True)
    attempt_id: Mapped[int] = mapped_column(ForeignKey("attempts.id"))
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    selected_option_ids: Mapped[list] = mapped_column(JSON, default=list)
    text_answer: Mapped[str] = mapped_column(Text, default="")
    # None — открытый ответ ждёт ручной проверки
    is_correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    attempt: Mapped[Attempt] = relationship(back_populates="answers")
    question: Mapped[Question] = relationship()


class BlockProgress(Base):
    __tablename__ = "block_progress"
    __table_args__ = (UniqueConstraint("user_id", "block_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    block_id: Mapped[int] = mapped_column(ForeignKey("blocks.id"))
    last_slide: Mapped[int] = mapped_column(Integer, default=0)
    viewed: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)
