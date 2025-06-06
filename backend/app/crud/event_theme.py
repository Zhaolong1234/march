from sqlalchemy.orm import Session
from app.schemas.event_theme import EventThemeCreate
from app.models.event_theme import EventTheme
from app.schemas.event_theme import EventSlotCreate,ParticipationCreate,SlotUpdate,themeUpdate

from app.models.event_theme import EventSlot,Participation
from fastapi import HTTPException
def get_all_themes(db: Session):
    return db.query(EventTheme).all()

def create_theme(db: Session, theme: EventThemeCreate):
    db_theme = EventTheme(**theme.dict())
    db.add(db_theme)
    db.commit()
    db.refresh(db_theme)
    return db_theme

def get_theme(db: Session, theme_id: int):
    return db.query(EventTheme).filter(EventTheme.id == theme_id).first()

def delete_theme(db:Session,theme_id:int):
    theme = db.query(EventTheme).filter(EventTheme.id == theme_id).first()
    slots = db.query(EventSlot).filter(EventSlot.theme_id == theme_id).all()
    for slot in slots:
        db.query(Participation).filter(Participation.slot_id == slot.id).delete()
    if not theme:
        raise HTTPException(status_code=404, detail="Theme not found")
    db.query(EventSlot).filter(EventSlot.theme_id == theme_id).delete()
    db.delete(theme)
    db.commit()
    return {"detail: Theme already have been deleted"}

def update_theme(db: Session, theme_id: int, theme: themeUpdate):
    db_theme = db.query(EventTheme).filter(EventTheme.id == theme_id).first()
    if not db_theme:
        raise HTTPException(status_code=404, detail="Theme not found")
    
    update_data = theme.dict(exclude_unset=True)  # 只更新有值的字段
    
    for key, value in update_data.items():
        setattr(db_theme, key, value)

    db.commit()
    db.refresh(db_theme)
    return db_theme



def create_slot(db: Session, slot: EventSlotCreate):
    db_slot = EventSlot(
        theme_id=slot.theme_id,
        date=slot.date,
        time=slot.time,
        max_people=slot.max_people
    )
    db.add(db_slot)
    db.commit()
    db.refresh(db_slot)
    return db_slot

def get_slots(db:Session):
    return db.query(EventSlot).all()

def get_slot(db: Session, slot_id: int):
    return db.query(EventSlot).filter(EventSlot.id == slot_id).first()
    
def update_slot(db: Session, slot_id: int, slot: SlotUpdate):
    db_slot = get_slot(db, slot_id)
    if not db_slot:
        return None

    for key, value in slot.dict(exclude_unset=True).items():
        setattr(db_slot, key, value)

    db.commit()
    db.refresh(db_slot)
    return db_slot


def delete_slot(db:Session,slot_id: int):
    db_slot = get_slot(db,slot_id)
    if not db_slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    db.delete(db_slot)
    db.commit()
    return {"message": "Slot deleted successfully"}


# 在 crud/event_theme.py 中添加
from sqlalchemy import literal, cast, String, Integer, Date, Time

def get_slot_cards(db: Session):
    # 查询有 slot 的数据
    query_with_slots = (
        db.query(
            EventSlot.id.label("slotid"),
            EventSlot.theme_id.label("themeid"),
            EventSlot.date,
            EventSlot.time,
            EventSlot.max_people.label("maxpeople"),
            EventTheme.title.label("name"),
            EventTheme.image_url.label("imageUrl")
        )
        .join(EventTheme, EventTheme.id == EventSlot.theme_id)
    )

    # 查询没有 slot 的主题，补 null 值（必须明确类型）
    query_without_slots = (
        db.query(
            literal(None).cast(Integer).label("slotid"),
            EventTheme.id.label("themeid"),
            literal(None).cast(Date).label("date"),
            literal(None).cast(Time).label("time"),
            literal(None).cast(Integer).label("maxpeople"),
            EventTheme.title.label("name"),
            EventTheme.image_url.label("imageUrl")
        )
        .filter(~EventTheme.slots.any())
    )

    results = query_with_slots.union_all(query_without_slots).all()
    return [dict(r._mapping) for r in results]



def create_participation(db: Session, participation: ParticipationCreate, user_id: int):
    slot = db.query(EventSlot).filter(EventSlot.id == participation.slot_id).first()
    if not slot:
        raise HTTPException(status_code=404, detail="时间段不存在")

    new_part = Participation(
        slot_id=participation.slot_id,
        name=participation.name,
        email=participation.email,
        user_id=user_id
    )
    db.add(new_part)
    db.commit()
    db.refresh(new_part)
    return new_part
