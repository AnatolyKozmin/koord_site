from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user, require_roles
from ..models import Block, HomeworkCheck, HomeworkSubmission, Slide, User, UserRole
from ..schemas import (
    HomeworkAnswerIn,
    HomeworkAnswerOut,
    HomeworkBoardOut,
    HomeworkCheckIn,
    HomeworkCoordinatorOut,
    HomeworkItemOut,
)

router = APIRouter(prefix="/homework", tags=["homework"])

trainer_only = require_roles(UserRole.SUPERADMIN, UserRole.TRAINING_COORDINATOR)


def _homework_slides(db: Session) -> list[tuple[Slide, Block]]:
    rows = db.execute(
        select(Slide, Block)
        .join(Block, Slide.block_id == Block.id)
        .where(Block.is_published, Slide.homework != "")
        .order_by(Block.position, Block.id, Slide.position)
    ).all()
    return [(s, b) for s, b in rows if s.homework.strip()]


@router.get("", response_model=HomeworkBoardOut)
def homework_board(db: Session = Depends(get_db), _: User = Depends(trainer_only)):
    items = [
        HomeworkItemOut(
            slide_id=s.id,
            block_id=b.id,
            block_title=b.title,
            slide_position=s.position,
            homework=s.homework,
        )
        for s, b in _homework_slides(db)
    ]
    slide_ids = {it.slide_id for it in items}

    checks: dict[int, list[int]] = {}
    for c in db.scalars(select(HomeworkCheck)).all():
        if c.slide_id in slide_ids:
            checks.setdefault(c.user_id, []).append(c.slide_id)

    answers: dict[int, list[HomeworkAnswerOut]] = {}
    for s in db.scalars(select(HomeworkSubmission)).all():
        if s.slide_id in slide_ids:
            answers.setdefault(s.user_id, []).append(
                HomeworkAnswerOut(
                    slide_id=s.slide_id, text=s.text, updated_at=s.updated_at
                )
            )

    coordinators = db.scalars(
        select(User).where(User.role == UserRole.COORDINATOR).order_by(User.full_name)
    ).all()
    return HomeworkBoardOut(
        items=items,
        coordinators=[
            HomeworkCoordinatorOut(
                user_id=u.id,
                full_name=u.full_name,
                email=u.email,
                is_active=u.is_active,
                checked_slide_ids=checks.get(u.id, []),
                answers=answers.get(u.id, []),
            )
            for u in coordinators
        ],
    )


@router.post("/answer")
def submit_answer(
    body: HomeworkAnswerIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Координатор отправляет (или обновляет) текстовый ответ на домашку."""
    slide = db.get(Slide, body.slide_id)
    if slide is None or not slide.homework.strip():
        raise HTTPException(status_code=404, detail="У этого слайда нет домашки")
    if not slide.block.is_published:
        raise HTTPException(status_code=404, detail="Блок не опубликован")

    sub = db.scalar(
        select(HomeworkSubmission).where(
            HomeworkSubmission.user_id == user.id,
            HomeworkSubmission.slide_id == body.slide_id,
        )
    )
    if sub is None:
        sub = HomeworkSubmission(user_id=user.id, slide_id=body.slide_id)
        db.add(sub)
    sub.text = body.text.strip()
    db.commit()
    return {"ok": True}


@router.post("/check")
def set_homework_check(
    body: HomeworkCheckIn,
    db: Session = Depends(get_db),
    reviewer: User = Depends(trainer_only),
):
    target = db.get(User, body.user_id)
    if target is None or target.role != UserRole.COORDINATOR:
        raise HTTPException(status_code=404, detail="Координатор не найден")
    slide = db.get(Slide, body.slide_id)
    if slide is None or not slide.homework.strip():
        raise HTTPException(status_code=404, detail="У этого слайда нет домашки")

    check = db.scalar(
        select(HomeworkCheck).where(
            HomeworkCheck.user_id == body.user_id,
            HomeworkCheck.slide_id == body.slide_id,
        )
    )
    if body.done and check is None:
        db.add(
            HomeworkCheck(
                user_id=body.user_id, slide_id=body.slide_id, checked_by=reviewer.id
            )
        )
    elif not body.done and check is not None:
        db.delete(check)
    db.commit()
    return {"done": body.done}
