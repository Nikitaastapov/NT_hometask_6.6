from aiohttp import web
from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy_utils import EmailType
from bcrypt import hashpw, gensalt, checkpw
from sqlalchemy.exc import IntegrityError
import json
from sqlalchemy.future import select
PG_DSN = 'postgresql+asyncpg://app:1234@127.0.0.1:5431/app'
engine = create_async_engine(PG_DSN)
Session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()
# DB
class User(Base):
    __tablename__ = 'user_fields'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, index=True, unique=True)
    email = Column(EmailType, index=True, unique=True)
    password = Column(String(60), nullable=False)
    registration_time = Column(DateTime, server_default=func.now())
    billboards = relationship("Billboard", backref='user_fields')


class Billboard(Base):
    __tablename__ = 'billboard_fields'
    id = Column(Integer, primary_key=True, autoincrement=True)
    topic = Column(String, nullable=False, index=True, unique=True)
    description = Column(String, nullable=False, index=True, unique=True)
    user_id = Column(Integer, ForeignKey('user_fields.id', ondelete="CASCADE"))
    creation_time = Column(DateTime, server_default=func.now())


app = web.Application()
async def app_context(app):
#все, что написано для yield выполнится на старте, что после- после завершения
    print('start')
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    print('finish')

#Функция-обертка, которая открытвает сессию в начале request и закрывате в конце request
@web.middleware
async def session_middleware(request: web.Request, handler):
    async with Session() as session:
        request['session'] = session
        response = await handler(request)
        return response

app.cleanup_ctx.append(app_context)
#регистрируем middleware
app.middlewares.append(session_middleware)

async def get_user(user_id: int, session: Session):
    print('get_user works')
    user = await session.get(User, user_id)
    print(user)
    if user is None:
        raise web.HTTPNotFound(text=json.dumps({'status': 'error', 'message': 'user not found'}),
                               content_type='application/json')
    return user

async def get_password(user_password: str):
    password = user_password
    if len(password) < 6:
        raise (web.HTTPCreated(text=json.dumps({'status': 'error', 'message': 'password is too short'}),
                               content_type='application/json'))
    return password

async def get_article(billboard_id: int, session: Session):
    article = await session.get(Billboard, billboard_id)
    if article is None:
        raise web.HTTPNotFound(text=json.dumps({'status': 'error', 'message': 'article not found'}),
                               content_type='application/json')
    return article

# VIEW
class UserView(web.View):
    async def get(self):
        user = await get_user(int(self.request.match_info['user_id']), self.request['session'])
        return web.json_response({
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'registration_time': int(user.registration_time.timestamp())
        })
    async def post(self):
        json_data = await self.request.json()
        password = await get_password(json_data['password'])
        json_data['password'] = hashpw(password.encode(), salt=gensalt()).decode()
        user = User(**json_data)
        self.request['session'].add(user)
        try:
            await self.request['session'].commit()
        except IntegrityError as er:
            raise web.HTTPConflict(text=json.dumps({'error':'user already exists'}),
                                   content_type='application/json')
        return web.json_response({'id':user.id})

    async def patch(self):
        user = await get_user(int(self.request.match_info['user_id']), self.request['session'])
        json_data = await self.request.json()
        for field, value in json_data.items():
            setattr(user, field, value)
            self.request['session'].add(user)
            await self.request['session'].commit()
        return web.json_response({'status': 'success'})

    async def delete(self):
        user = await get_user(int(self.request.match_info['user_id']), self.request['session'])
        await self.request['session'].delete(user)
        await self.request['session'].commit()
        return web.json_response({'status': 'success'})

class BillboardView(web.View):
    async def get(self):
        billboard = await get_article(int(self.request.match_info['billboard_id']), self.request['session'])
        return web.json_response({
            'id': billboard.id,
            'topic': billboard.topic,
            'description': billboard.description,
            'creation_time': int(billboard.creation_time.timestamp())
        })
    async def post(self):
        json_data = await self.request.json()
        await get_user(int(json_data['user_id']), self.request['session'])
        billboard = Billboard(**json_data)
        self.request['session'].add(billboard)
        try:
            await self.request['session'].commit()
        except IntegrityError as er:
            raise web.HTTPConflict(text=json.dumps({'error':'article already exists'}),
                                   content_type='application/json')
        return web.json_response({'id':billboard.id})

    async def delete(self):
        billboard = await get_article(int(self.request.match_info['billboard_id']), self.request['session'])
        await self.request['session'].delete(billboard)
        await self.request['session'].commit()
        return web.json_response({'status': 'success'})


#ROUTES
app.add_routes([
    web.get('/user/{user_id:\d+}', UserView),
    web.post('/user/', UserView),
    web.patch('/user/{user_id:\d+}', UserView),
    web.delete('/user/{user_id:\d+}', UserView),
    web.post('/article/', BillboardView),
    web.get('/article/{billboard_id:\d+}', BillboardView),
    web.delete('/article/{billboard_id:\d+}', BillboardView),
])

if __name__ == '__main__':
    web.run_app(app)
