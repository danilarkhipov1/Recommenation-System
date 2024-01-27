from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, desc, func
from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import relationship
import os
import pickle
import pandas as pd
from sqlalchemy import create_engine


SQLALCHEMY_DATABASE_URL = "postgresql://robot-startml-ro:pheiph0hahj1Vaif@postgres.lab.karpov.courses:6432/startml"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Post(Base):
    __tablename__ = 'post'
    id = Column(Integer, primary_key=True)
    text = Column(String)
    topic = Column(String)
@app.get("/business_posts")
def get_business_posts(db: Session = Depends(get_db)):
    posts = db.query(Post).filter(Post.topic == "business").order_by(desc(Post.id)).limit(10).all()
    return [post.id for post in posts]


class User(Base):
    __tablename__='user'
    id = Column(Integer, primary_key=True)
    gender = Column(Integer)
    age = Column(Integer)
    country = Column(String)
    city = Column(String)
    exp_group = Column(Integer)
    os = Column(String)
    source = Column(String)

@app.get("/users_stats")
def get_users_stats(db: Session = Depends(get_db)):
    results = (
        db.query(User.country, User.os, func.count("*").label('count'))
        .filter(User.exp_group == 3)
        .group_by(User.country, User.os)
        .having(func.count() > 100)
        .order_by(desc(func.count("*")))
        .all()
    )
    return [(result.country, result.os, result.count) for result in results]
class Feed(Base):
    __tablename__ = 'feed_action'
    user_id = Column(Integer, ForeignKey(User.id), primary_key=True)
    post_id = Column(Integer, ForeignKey(Post.id), primary_key=True)
    action = Column(String)
    time = Column(TIMESTAMP)

    user = relationship("User")
    post = relationship("Post")
@app.get("/feed_actions/{user_id}")
def get_feed_actions(user_id: int, db: Session = Depends(get_db)):
    feed_actions = db.query(Feed).filter(Feed.user_id == user_id).all()
    return feed_actions
class UserGet(BaseModel):
    id: int
    gender: int
    age: int
    country: str
    city: str
    exp_group: int
    os: str
    source: str

    class Config:
        orm_mode = True

class PostGet(BaseModel):
    id: int
    text: str
    topic: str

    class Config:
        orm_mode = True

class FeedGet(BaseModel):
    user_id: int
    post_id: int
    action: str
    time: datetime
    user: UserGet
    post: PostGet

    class Config:
        orm_mode = True


# Зависимость для подключения к базе данных

# Endpoint для получения информации о действиях в ленте
@app.get("/feed/{user_id}", response_model=List[FeedGet])
def get_user_feed(user_id: int, db: Session = Depends(get_db)):
    feed_actions = db.query(Feed).filter(Feed.user_id == user_id).all()
    return feed_actions


@app.get("/user/{id}", response_model=UserGet)
def find_user(id: int, db: Session = Depends(get_db)) -> UserGet:
    result = db.query(User).filter(User.id == id).first()
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail='User not found')

@app.get("/post/{id}", response_model=PostGet)
def find_post(id: int, db: Session = Depends(get_db)) -> PostGet:
    result = db.query(Post).filter(Post.id == id).first()
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail='Post not found')

@app.get("/user/{id}/feed", response_model=List[FeedGet])
def find_user_feed(id: int, limit: int = 10, db: Session = Depends(get_db)) -> List[FeedGet]:
    result = db.query(Feed).filter(Feed.user_id == id).order_by(Feed.timestamp.desc()).limit(limit).all()
    if result:
        return result
    else:
        return []

@app.get("/post/{id}/feed", response_model=List[FeedGet])
def find_post_feed(id: int, limit: int = 10, db: Session = Depends(get_db)) -> List[FeedGet]:
    result = db.query(Feed).filter(Feed.post_id == id).order_by(Feed.timestamp.desc()).limit(limit).all()
    if result:
        return result
    else:
        return []

@app.get("/post/recommendations/", response_model=List[PostGet])
def get_post_recommendations(id: int, limit: int = 10, db: Session = Depends(get_db)) -> List[PostGet]:
    result = (db.query(Post)
                .select_from(Feed)
                .filter(Feed.action == 'like')
                .join(Post)
                .group_by(Post.id)
                .order_by(desc(func.count(Post.id)))
                .limit(limit)
                .all())

    if result:
        return result
    else:
        return []


#МОДЕЛЬКА
def get_model_path(path: str) -> str:
    if os.environ.get("IS_LMS") == "1":  # Проверка среды выполнения
        MODEL_PATH = '/workdir/user_input/model'
    else:
        MODEL_PATH = path
    return MODEL_PATH


#Функция для загрузки тестовой модели
def load_models_test():
    model_path = get_model_path_test("D:/StartML_KarpovCourses/1st_catboost_model.cbm")
    #model_path = get_model_path_test("/my/super/path")
    # LOAD MODEL HERE PLS :)
    from_file =  CatBoostClassifier()  # здесь не указываем параметры, которые были при обучении, в дампе модели все есть
    from_file.load_model(model_path)
    return from_file

#Функция для загрузки контрольной модели
def load_models_control():
    model_path = get_model_path_control("D:/StartML_KarpovCourses/catboost_model_with_TDF.cbm")
    #model_path = get_model_path_control("/my/super/path")
    # LOAD MODEL HERE PLS :)
    from_file =  CatBoostClassifier()  # здесь не указываем параметры, которые были при обучении, в дампе модели все есть
    from_file.load_model(model_path)
    return from_file

#Загрузка моделей
model_control = load_models_control()
print(model_control)
model_test = load_models_test()
print(model_test)


def batch_load_sql(query: str) -> pd.DataFrame:
    CHUNKSIZE = 10000
    engine = create_engine(
        "postgresql://robot-startml-ro:pheiph0hahj1Vaif@"
        "postgres.lab.karpov.courses:6432/startml"
    )
    conn = engine.connect().execution_options(stream_results=True)
    chunks = []
    for chunk_dataframe in pd.read_sql(query, conn, chunksize=CHUNKSIZE):
        chunks.append(chunk_dataframe)
    conn.close()
    return pd.concat(chunks, ignore_index=True)

def load_features() -> pd.DataFrame:
    query = """
    SELECT u.*, f.timestamp, f.post_id, f.target 
    FROM user_data u 
    LEFT JOIN LATERAL (
        SELECT *,
        ROW_NUMBER() OVER(PARTITION BY user_id) AS order
        FROM feed_data
    ) f on u.user_id = f.user_id
    WHERE f.order <= 10 AND f.action != 'like'
    """
    return batch_load_sql(query)

# Загрузка признаков
features = load_features()
