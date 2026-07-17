from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..database import get_db
from ..deps import get_current_user, require_roles
from ..models import (
    Attempt,
    AttemptStatus,
    Block,
    BlockProgress,
    HomeworkCheck,
    HomeworkSubmission,
    Slide,
    User,
    UserRole,
)
from ..schemas import (
    BlockCreate,
    BlockDetail,
    BlockListItem,
    BlockUpdate,
    ProgressIn,
    ProgressOut,
    SlideIn,
    SlideOut,
)

router = APIRouter(prefix="/blocks", tags=["blocks"])

editor_only = require_roles(UserRole.SUPERADMIN, UserRole.TRAINING_COORDINATOR)

# приоритет статусов попыток: показываем лучший результат
_STATUS_RANK = {
    AttemptStatus.PASSED: 2,
    AttemptStatus.PENDING_REVIEW: 1,
    AttemptStatus.FAILED: 0,
}


def is_editor(user: User) -> bool:
    return user.role in (UserRole.SUPERADMIN, UserRole.TRAINING_COORDINATOR)


def best_test_status(db: Session, user_id: int, test_id: int) -> AttemptStatus | None:
    statuses = db.scalars(
        select(Attempt.status).where(
            Attempt.user_id == user_id, Attempt.test_id == test_id
        )
    ).all()
    if not statuses:
        return None
    return max(statuses, key=lambda s: _STATUS_RANK[s])


def _checked_slide_ids(db: Session, user_id: int, block: Block) -> set[int]:
    """id слайдов блока, за которые пользователю зачтена домашка."""
    slide_ids = [s.id for s in block.slides if s.homework.strip()]
    if not slide_ids:
        return set()
    return set(
        db.scalars(
            select(HomeworkCheck.slide_id).where(
                HomeworkCheck.user_id == user_id,
                HomeworkCheck.slide_id.in_(slide_ids),
            )
        ).all()
    )


def _progress_for(db: Session, user: User, block: Block) -> ProgressOut:
    prog = db.scalar(
        select(BlockProgress).where(
            BlockProgress.user_id == user.id, BlockProgress.block_id == block.id
        )
    )
    test_status = best_test_status(db, user.id, block.test.id) if block.test else None
    return ProgressOut(
        last_slide=prog.last_slide if prog else 0,
        viewed=prog.viewed if prog else False,
        test_status=test_status,
        homework_done=len(_checked_slide_ids(db, user.id, block)),
    )


def _to_list_item(db: Session, user: User, block: Block) -> BlockListItem:
    return BlockListItem(
        id=block.id,
        title=block.title,
        description=block.description,
        kind=block.kind,
        position=block.position,
        is_published=block.is_published,
        slide_count=len(block.slides),
        has_test=block.test is not None,
        homework_total=sum(1 for s in block.slides if s.homework.strip()),
        progress=_progress_for(db, user, block),
    )


def _get_block(db: Session, block_id: int, user: User) -> Block:
    block = db.get(
        Block, block_id, options=[selectinload(Block.slides), selectinload(Block.test)]
    )
    if block is None or (not block.is_published and not is_editor(user)):
        raise HTTPException(status_code=404, detail="Блок не найден")
    return block


@router.get("", response_model=list[BlockListItem])
def list_blocks(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    query = (
        select(Block)
        .options(selectinload(Block.slides), selectinload(Block.test))
        .order_by(Block.position, Block.id)
    )
    if not is_editor(user):
        query = query.where(Block.is_published)
    return [_to_list_item(db, user, b) for b in db.scalars(query).all()]


@router.post("", response_model=BlockListItem, status_code=status.HTTP_201_CREATED)
def create_block(
    body: BlockCreate,
    db: Session = Depends(get_db),
    user: User = Depends(editor_only),
):
    max_pos = max((p for p in db.scalars(select(Block.position)).all()), default=-1)
    block = Block(
        title=body.title,
        description=body.description,
        kind=body.kind,
        position=max_pos + 1,
    )
    db.add(block)
    db.commit()
    db.refresh(block)
    return _to_list_item(db, user, block)


@router.get("/{block_id}", response_model=BlockDetail)
def get_block(
    block_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    block = _get_block(db, block_id, user)
    item = _to_list_item(db, user, block)
    checked = _checked_slide_ids(db, user.id, block)
    slide_ids = [s.id for s in block.slides]
    my_answers = {
        sub.slide_id: sub.text
        for sub in db.scalars(
            select(HomeworkSubmission).where(
                HomeworkSubmission.user_id == user.id,
                HomeworkSubmission.slide_id.in_(slide_ids),
            )
        ).all()
    } if slide_ids else {}
    slides = []
    for s in block.slides:
        out = SlideOut.model_validate(s)
        out.homework_done = s.id in checked
        out.homework_answer = my_answers.get(s.id, "")
        slides.append(out)
    return BlockDetail(**item.model_dump(), slides=slides)


@router.patch("/{block_id}", response_model=BlockListItem)
def update_block(
    block_id: int,
    body: BlockUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(editor_only),
):
    block = _get_block(db, block_id, user)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(block, field, value)
    db.commit()
    db.refresh(block)
    return _to_list_item(db, user, block)


@router.delete("/{block_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_block(
    block_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(editor_only),
):
    block = _get_block(db, block_id, user)
    db.delete(block)
    db.commit()


@router.put("/{block_id}/slides", response_model=list[SlideOut])
def replace_slides(
    block_id: int,
    body: list[SlideIn],
    db: Session = Depends(get_db),
    user: User = Depends(editor_only),
):
    """Заменяет набор слайдов блока. Существующие слайды (по id) обновляются,
    а не пересоздаются — иначе слетали бы отметки о проверке домашек."""
    block = _get_block(db, block_id, user)
    existing = {s.id: s for s in block.slides}
    for i, data in enumerate(body):
        slide = existing.pop(data.id, None) if data.id else None
        if slide is None:
            slide = Slide(block_id=block.id)
            db.add(slide)
        slide.position = i
        slide.type = data.type
        slide.content = data.content
        slide.media_url = data.media_url
        slide.homework = data.homework
    for leftover in existing.values():
        db.delete(leftover)  # каскадом удаляет и homework_checks
    db.commit()
    db.refresh(block)
    return [SlideOut.model_validate(s) for s in block.slides]


@router.post("/{block_id}/progress", response_model=ProgressOut)
def save_progress(
    block_id: int,
    body: ProgressIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    block = _get_block(db, block_id, user)
    if not block.slides:
        return _progress_for(db, user, block)
    prog = db.scalar(
        select(BlockProgress).where(
            BlockProgress.user_id == user.id, BlockProgress.block_id == block.id
        )
    )
    if prog is None:
        prog = BlockProgress(user_id=user.id, block_id=block.id, last_slide=0, viewed=False)
        db.add(prog)
    last = min(body.last_slide, len(block.slides) - 1)
    prog.last_slide = max(prog.last_slide, last)
    if prog.last_slide >= len(block.slides) - 1:
        prog.viewed = True
    db.commit()
    return _progress_for(db, user, block)
