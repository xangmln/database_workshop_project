from app.api.utils.deps import SessionDep
from app.api.models.tag import Tag
from app.api.schemas.tags import TagOut

async def get_tag_by_word(db: SessionDep, word: str) -> TagOut:
    tag = db.query(Tag).filter(Tag.word == word).first()
    if tag:
        return TagOut.model_validate(tag)
    else:
        new_tag = Tag(word=word)
        db.add(new_tag)
        db.flush()
        return TagOut.model_validate(new_tag)