from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..database import get_db
from ..deps import require_roles
from ..models import Attempt, Block, BlockProgress, User, UserRole
from ..schemas import (
    BlockResult,
    CoordinatorResult,
    ResultsBlockRef,
    ResultsOut,
)
from .blocks import _STATUS_RANK

router = APIRouter(prefix="/results", tags=["results"])

trainer_only = require_roles(UserRole.SUPERADMIN, UserRole.TRAINING_COORDINATOR)


@router.get("", response_model=ResultsOut)
def results(db: Session = Depends(get_db), _: User = Depends(trainer_only)):
    blocks = db.scalars(
        select(Block)
        .options(selectinload(Block.slides), selectinload(Block.test))
        .where(Block.is_published)
        .order_by(Block.position, Block.id)
    ).all()

    coordinators = db.scalars(
        select(User).where(User.role == UserRole.COORDINATOR).order_by(User.full_name)
    ).all()

    # прогресс по блокам: (user_id, block_id) -> BlockProgress
    prog_map = {
        (p.user_id, p.block_id): p
        for p in db.scalars(select(BlockProgress)).all()
    }

    # лучший статус попытки: (user_id, test_id) -> status
    best_status: dict[tuple[int, int], object] = {}
    for a in db.scalars(select(Attempt)).all():
        key = (a.user_id, a.test_id)
        cur = best_status.get(key)
        if cur is None or _STATUS_RANK[a.status] > _STATUS_RANK[cur]:
            best_status[key] = a.status

    out_coordinators = []
    for u in coordinators:
        per_block = []
        blocks_done = 0
        slides_viewed = 0
        tests_passed = 0
        pct_sum = 0

        for b in blocks:
            slide_count = len(b.slides)
            prog = prog_map.get((u.id, b.id))
            test_status = best_status.get((u.id, b.test.id)) if b.test else None

            if prog and prog.viewed:
                viewed_slides = slide_count
            elif prog:
                viewed_slides = min(prog.last_slide + 1, slide_count)
            else:
                viewed_slides = 0

            percent = round(viewed_slides / slide_count * 100) if slide_count else 0
            slides_viewed += viewed_slides
            pct_sum += percent

            # блок завершён: если есть тест — сдан; иначе просмотрен до конца
            done = (
                test_status is not None and test_status.value == "passed"
                if b.test
                else bool(prog and prog.viewed)
            )
            if done:
                blocks_done += 1
            if test_status is not None and test_status.value == "passed":
                tests_passed += 1

            per_block.append(
                BlockResult(
                    block_id=b.id,
                    title=b.title,
                    kind=b.kind,
                    percent=percent,
                    viewed=bool(prog and prog.viewed),
                    test_status=test_status,
                )
            )

        out_coordinators.append(
            CoordinatorResult(
                user_id=u.id,
                full_name=u.full_name,
                email=u.email,
                is_active=u.is_active,
                blocks_done=blocks_done,
                slides_viewed=slides_viewed,
                tests_passed=tests_passed,
                overall_percent=round(pct_sum / len(blocks)) if blocks else 0,
                per_block=per_block,
            )
        )

    return ResultsOut(
        blocks=[ResultsBlockRef(id=b.id, title=b.title, kind=b.kind) for b in blocks],
        coordinators=out_coordinators,
    )
