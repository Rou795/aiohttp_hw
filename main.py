import json
from typing import Type

import bcrypt
from aiohttp import web
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models import Base, Session, User, engine, Ad
from schema import CreateUser, UpdateUser, CreateAd, UpdateAd

app = web.Application()


# проверка валидности данных, переданных в запросе
def validate_json(json_data: dict, schema_class: Type[CreateUser] | Type[UpdateUser] | Type[CreateAd] | Type[UpdateAd]):
    try:
        return schema_class(**json_data).dict(exclude_unset=True)
    except ValidationError as er:
        error = er.errors()[0]
        error.pop("ctx", None)
        raise get_http_error(web.HTTPConflict, "Bad data. Check them, please.")


# хэширование пароля
def hash_password(password: str):
    password = password.encode()
    password = bcrypt.hashpw(password, bcrypt.gensalt())
    password = password.decode()
    return password


# проверка пароля
def check_password(password: str, hashed_password: str):
    password = password.encode()
    hashed_password = hashed_password.encode()
    return bcrypt.checkpw(password, hashed_password)


async def orm_context(app):
    print("START")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()
    print("FINISH")


app.cleanup_ctx.append(orm_context)


# функция для формирования ошибки клиенту
def get_http_error(error_class, message):
    response = json.dumps({"error": message})
    http_error = error_class(text=response, content_type="application/json")
    return http_error


async def get_user_by_id(session, user_id):
    user = await session.get(User, user_id)
    if user is None:
        raise get_http_error(web.HTTPNotFound, f"User with id {user_id} not found")
    return user


async def get_ad_by_id(session, ad_id):
    ad = await session.get(Ad, ad_id)
    if ad is None:
        raise get_http_error(web.HTTPNotFound, f"Ad with id {ad_id} not found")
    return ad


async def add_user(session, user):
    try:
        session.add(user)
        await session.commit()
    except IntegrityError:
        print(get_user_by_id(session, user.dict))
        raise get_http_error(
            web.HTTPConflict, f"User with name {user.name} already exists"
        )


async def add_ad(session, ad):
    try:
        session.add(ad)
        await session.commit()
    except IntegrityError:
        print(get_ad_by_id(session, ad.dict))
        raise get_http_error(
            web.HTTPConflict, f"Ad with name {ad.title} already exists"
        )


@web.middleware
async def session_middleware(request, handler):
    async with Session() as session:
        request.session = session
        response = await handler(request)
        return response


app.middlewares.append(session_middleware)


def avtorization(password: str, user_id: str):
    if password is not None:
        return check_password(password, get_user_by_id(user_id).password)
    else:
        return False


# класс для обработки запросов, касающихся модели User
class UserView(web.View):

    @property
    def user_id(self):
        return int(self.request.match_info["user_id"])

    @property
    def session(self) -> AsyncSession:
        return self.request.session

    async def get_user(self):
        user = await get_user_by_id(self.session, self.user_id)
        return user

    async def get(self):
        user = await self.get_user()
        return web.json_response(user.dict)

    async def post(self):
        json_data = validate_json(await self.request.json(), CreateUser)
        json_data["password"] = hash_password(json_data["password"])

        user = User(**json_data)
        await add_user(self.session, user)
        return web.json_response(
            {
                "id": user.id,
            }
        )

    async def patch(self):
        json_data = validate_json(await self.request.json(), UpdateUser)
        headers = self.request.headers
        user_id = headers.get('user_id', None)
        if user_id is None:
            raise get_http_error(web.HTTPConflict, "Need avtorization.")
        else:
            user_id = int(user_id)
            user = await get_user_by_id(self.session, user_id)
            if check_password(headers.get('password', None), user.password):
                if "password" in json_data:
                    json_data["password"] = hash_password(json_data["password"])
                user = await self.get_user()
                for field, value in json_data.items():
                    setattr(user, field, value)
                await add_user(self.session, user)
                return web.json_response(
                    {
                        "id": user.id,
                    }
                )
            else:
                raise get_http_error(web.HTTPConflict, "Bad avtorization.")

    async def delete(self):
        headers = self.request.headers
        user_id = headers.get('user_id', None)
        if user_id is None:
            raise get_http_error(web.HTTPConflict, "Need avtorization.")
        else:
            user = await get_user_by_id(self.session, int(user_id))
            if check_password(headers.get('password', None), user.password):
                await self.session.delete(user)
                await self.session.commit()
                return web.json_response({"status": "deleted"})
            else:
                raise get_http_error(web.HTTPConflict, "Bad avtorization.")


# класс для обработки запросов, касающихся модели Ad
class AdView(web.View):

    @property
    def ad_id(self):
        return int(self.request.match_info["ad_id"])

    @property
    def session(self) -> AsyncSession:
        return self.request.session

    async def get_ad(self):
        ad = await get_ad_by_id(self.session, self.ad_id)
        return ad

    async def get(self):
        ad = await self.get_ad()
        return web.json_response(ad.dict)

    async def post(self):
        json_data = validate_json(await self.request.json(), CreateAd)
        headers = self.request.headers
        user_id = headers.get('user_id', None)
        if user_id is None:
            return get_http_error(web.HTTPConflict, 'Need avtorization.')
        else:
            user = await get_user_by_id(self.session, int(user_id))
            if check_password(headers.get('password', None), user.password):
                ad = Ad(**json_data)
                ad.user_id = int(ad.user_id)
                await add_ad(self.session, ad)
                return web.json_response(
                    {
                        "id": ad.id,
                        "title": ad.title,
                        "user_id": user_id,
                    }
                )
            else:
                get_http_error(web.HTTPConflict, "Bad avtorization")

    async def patch(self):
        json_data = validate_json(await self.request.json(), UpdateAd)
        headers = self.request.headers
        user_id = headers.get('user_id', None)
        if user_id is None:
            return get_http_error(web.HTTPConflict, 'Need avtorization.')
        else:
            user = await get_user_by_id(self.session, int(user_id))
            if check_password(headers['password'], user.password):
                ad = await self.get_ad()
                for field, value in json_data.items():
                    setattr(ad, field, value)
                await add_ad(self.session, user)
                return web.json_response(
                    {
                        "id": user.id,
                    }
                )
            else:
                get_http_error(web.HTTPConflict, "Bad avtorization")

    async def delete(self):
        headers = self.request.headers
        user_id = headers.get('user_id', None)
        if user_id is None:
            return get_http_error(web.HTTPConflict, 'Need avtorization.')
        else:
            user = await get_user_by_id(self.session, int(user_id))
            if check_password(headers['password'], user.password):
                ad = await self.get_ad()
                await self.session.delete(ad)
                await self.session.commit()
                return web.json_response({"status": "deleted"})
            else:
                get_http_error(web.HTTPConflict, "Bad avtorization")


app.add_routes(
    [
        web.get("/user/{user_id:\d+}", UserView),
        web.patch("/user/{user_id:\d+}", UserView),
        web.delete("/user/{user_id:\d+}", UserView),
        web.post("/user", UserView),

        web.get("/ad/{ad_id:\d+}", AdView),
        web.patch("/ad/{ad_id:\d+}", AdView),
        web.delete("/ad/{ad_id:\d+}", AdView),
        web.post("/ad", AdView),
    ]
)

if __name__ == "__main__":
    web.run_app(app)
