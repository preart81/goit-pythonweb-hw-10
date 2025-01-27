# Зберігання та управління контактами

## Клонуємо попередню версію

Встановимо залежності

```shell
poetry install
```

src\database\models.py

- додаємо клас User
- і залежність user в клас Contact
- якщо ми створили нову базу даних - спочатку застосуємо готові міграції
  ```shell
  alembic upgrade head
  ```
- створюємо міграцію наступною консольною командою в корені проєкту:
  ```Shell
  alembic revision --autogenerate -m 'add user'
  ```
  > Саме оточення alembic ініціалізовано в попередньому проекті
  > Ініціалізуємо оточення `alembic` з підтримкою асинхронності `-t async`
  >
  > ```shell
  > alembic init -t async alembic
  > ```
- Якщо файл з міграцією успішно створився в директорії migrations/versions, то застосуємо створену міграцію:
  ```shell
  alembic upgrade head
  ```
- перевіримо що поля і таблиця User створені:  
  ![alt text](md.media/001.png)

- створюємо схему валідації для users  
  [src/schemas/users.py](src/schemas/users.py)

- створюємо репозиторій для users
  [src/repository/users.py](src/repository/users.py)

## Додаємо сервіс автентифікації та користувача

Для правильної роботи нашого сервісу необхідно встановити наступні пакети:

```shell
    poetry add python-jose["cryptography"]
    poetry add passlib["bcrypt"]
```

- додаємо параметри `jwt` в [src/conf/config.py](src/conf/config.py)
- додаємо код сервісу [src/services/users.py](src/services/users.py)
- додаємо код сервісу [src/services/auth.py](src/services/auth.py)

## Додаємо маршрути автентифікації та користувача

- Створимо маршрути [src/api/auth.py](src/api/auth.py) та додамо:
  - `/api/auth/register` — маршрут для реєстрації користувача;
  - `/api/auth/login` — маршрут для входу користувача;
- підключити нові роутери у головному файлі застосунку `main.py`

## Додаємо авторизацію

- У модель User необхідно додати поле `confirmed = Column(Boolean, default=False)`. Це логічний вираз, що визначає, чи був підтверджений email користувача.
- Після цього необхідно виконати міграції для зміни таблиці користувача.
  ```shell
  alembic revision --autogenerate -m 'add to model User filed confirmed'
  ```
- Та застосувати їх.

  ```shell
  alembic upgrade head
  ```

- додамо в репозиторій [src/repository/contacts.py](src/repository/contacts.py) додатковий параметр user: User. Це дозволяє нам виконувати операції в контексті автентифікованого користувача. У кожному методі ми оновили SQLAlchemy-запити, щоб вони враховували контекст користувача. Це гарантує, що користувачі можуть взаємодіяти лише зі своїми конатктами.

## Додаємо ratelimit

Обмежимо кількість запитів до маршруту користувача `/me`

- додаємо ліміти в [src/api/users.py](src/api/users.py) і огортаємо /me декоратором

  ```py
  limiter = Limiter(key_func=get_remote_address)

  @router.get("/me", response_model=User)
  @limiter.limit("5/minute")
  async def me(request: Request, user: User = Depends(get_current_user)):
      return user
  ```

- додаємо обробник винятків у [main.py](main.py)
  ```Py
  @app.exception_handler(RateLimitExceeded)
  async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
      return JSONResponse(
          status_code=429,
          content={"error": "Перевищено ліміт запитів. Спробуйте пізніше."},
      )
  ```

## Вмикаємо CORS

Для використання CORS у FastAPI ми імпортуємо `CORSMiddleware` з пакета `fastapi`:

```Py
from fastapi import FastAPIfrom fastapi.middleware.cors import CORSMiddleware
```

Створюємо екземпляр застосунку:

```Py
app = FastAPI()
```

Визначаємо список доменів, які можуть надсилати запити до нашого API:

```Py
origins = [ "<http://localhost:3000>" ]
```

Додаємо `CORSMiddleware` у наш застосунок:

```Py
app.add_middleware( CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"],)
```

## Запуск

Щоб запустити програму FastAPI для розробки, можна використати `fastapi dev` команду:

    fastapi dev main.py

Або, щоб більш гнучко налаштовувати запуск, можна виконати наступну команду, щоб запустити сервер `FastAPI` з `uvicorn`:

    uvicorn main:app --host localhost --port 8000 --reload

Тут параметри команди мають наступне значення:

- `uvicorn` — високопродуктивний вебсервер ASGI;
- `main` — файл `main.py`;
- `app` — об'єкт, повернений після запиту `app = FastAPI()`;
- `-host` — дозволяє прив'язати сокет до хоста. Значення за замовчуванням — `127.0.0.1`;
- `-port` — дозволяє прив'язати сокет до певного порту. За замовчуванням використовується значення `8000`;
- `-reload` — забезпечує гаряче перезавантаження сервера під час розробки.
