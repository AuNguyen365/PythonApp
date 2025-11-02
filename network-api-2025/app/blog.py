from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from app.database import Blog, User, get_db
from app.utils import decode_token, parse_bearer, response, clamp_pagination

router = APIRouter(prefix="/blog", tags=["Blog"])


# ---- Helpers ----


def get_current_user(authorization: str | None, db: Session) -> User:
    token = parse_bearer(authorization)
    try:
        user_id = int(decode_token(token).get("sub"))
        user = db.query(User).get(user_id)
        if not user:
            raise HTTPException(status_code=401, detail="Không tìm thấy người dùng")
        return user
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Token không hợp lệ")


SORT_FIELDS = {
    "created_at": Blog.created_at,
    "title": Blog.title,
}

# ---- Public ----
@router.get("/list")
def list_blogs(
    q: str = "",
    sort: str = Query("-created_at", description="created_at|title, tiền tố '-' = giảm dần"),
    offset: int | None = 0,
    limit: int | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(Blog)
    if q:
        query = query.filter((Blog.title.contains(q)) | (Blog.content.contains(q)))


# sort
    direction = desc if sort.startswith("-") else asc
    field_key = sort[1:] if sort.startswith("-") else sort
    col = SORT_FIELDS.get(field_key, Blog.created_at)
    query = query.order_by(direction(col))


    total = query.count()
    offset, limit = clamp_pagination(offset, limit)
    items = query.offset(offset).limit(limit).all()


    data = [{
        "id": b.id,
        "title": b.title,
        "created_at": b.created_at,
        "author": b.author.fullname if b.author else None
    } for b in items]
    return response("success", "Danh sách bài viết", data, meta={"offset": offset, "limit": limit, "total": total})


@router.get("/{blog_id}")
def get_blog(blog_id: int, db: Session = Depends(get_db)):
    b = db.query(Blog).get(blog_id)
    if not b:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài viết")
    return response("success", "Chi tiết bài viết", {
        "id": b.id, "title": b.title, "content": b.content,
        "created_at": b.created_at,
        "author": b.author.fullname if b.author else None
})

# ---- Private (Bearer) ----
@router.post("/create")
def create_blog(
    title: str, content: str,
    authorization: str | None = Header(None),
    db: Session = Depends(get_db)
):
    user = get_current_user(authorization, db)
    blog = Blog(title=title, content=content, author_id=user.id)
    db.add(blog)
    db.commit()
    return response("success", "Tạo bài viết thành công", {"id": blog.id})


@router.put("/{blog_id}")
def update_blog(
    blog_id: int, title: str | None = None, content: str | None = None,
    authorization: str | None = Header(None),
    db: Session = Depends(get_db)
):
    user = get_current_user(authorization, db)
    blog = db.query(Blog).get(blog_id)
    if not blog:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài viết")
    if blog.author_id != user.id:
        raise HTTPException(status_code=403, detail="Không có quyền sửa")
    if title is not None:
        blog.title = title
    if content is not None:
        blog.content = content
    db.commit()
    return response("success", "Cập nhật thành công")

@router.delete("/{blog_id}")
def delete_blog(
    blog_id: int,
    authorization: str | None = Header(None),
    db: Session = Depends(get_db)
):
    user = get_current_user(authorization, db)
    blog = db.query(Blog).get(blog_id)
    if not blog:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài viết")
    if blog.author_id != user.id:
        raise HTTPException(status_code=403, detail="Không có quyền xoá")
    db.delete(blog)
    db.commit()
    return response("success", "Xoá thành công")