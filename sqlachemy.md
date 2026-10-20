这是一份为你整理的 **SQLAlchemy 2.0 学习手册**。

结合你之前的开发习惯，这份手册会重点围绕 **Python 后端开发**（特别是配合 FastAPI 使用）以及 **ORM 映射**（你之前遇到的 `DeclarativeBase` 问题）来展开。

---

### 📚 一、SQLAlchemy 是什么？

简单来说，SQLAlchemy 是 Python 生态中最成熟的 **ORM（对象关系映射）框架**。它就像一座桥，让你通过操作 Python 对象（类、实例）来间接操作数据库，而无需手写大量原生 SQL 字符串。

**核心优势：**
*   **跨数据库兼容：** 一套代码无缝适配 MySQL、PostgreSQL、SQLite 等（只需改连接串）。
*   **防注入：** 自动参数化查询，天然防止 SQL 注入。
*   **开发效率高：** 配合 PyCharm 等工具，拥有极佳的代码补全和类型提示体验。

---

### 🏗️ 二、核心架构：Core 与 ORM

SQLAlchemy 分为两层，日常后端开发主要使用上层的 ORM：

1.  **Core（底层核心）：** 负责 SQL 表达式构建、数据库连接池管理、方言适配。
2.  **ORM（上层封装）：** 建立在 Core 之上，提供对象关系映射，让你用面向对象的方式操作数据库。

---

### 🛠️ 三、环境搭建与基础配置

#### 1. 安装依赖
```bash
# 安装 SQLAlchemy 核心
pip install sqlalchemy
# 安装数据库驱动（根据你的数据库二选一）
pip install pymysql          # MySQL 驱动
pip install psycopg2-binary  # PostgreSQL 驱动
```

#### 2. 统一配置（db.py）
在实际项目中，建议将引擎、会话工厂和基类集中管理：

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# 1. 数据库连接字符串
# 格式：数据库类型+驱动://用户名:密码@地址:端口/数据库名
DB_URL = "mysql+pymysql://root:123456@localhost:3306/mydb?charset=utf8mb4"

# 2. 创建引擎（echo=True 会在控制台打印底层SQL，方便调试）
engine = create_engine(DB_URL, echo=True)

# 3. 创建会话工厂
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# 4. 声明式基类（这就是你之前遇到的 DeclarativeBase）
class Base(DeclarativeBase):
    pass
```

---

### 📝 四、定义模型（Model）

在 SQLAlchemy 2.0 中，推荐使用 `Mapped` 和 `mapped_column` 来定义字段，这样能获得更好的类型提示：

```python
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from db import Base

class User(Base):
    __tablename__ = "users"  # 数据库中的表名

    # 主键 ID
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # 用户名，非空，最大长度50
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    # 年龄，带默认值
    age: Mapped[int] = mapped_column(default=18)
```

---

### 💻 五、CRUD 操作（增删改查）

所有的数据库操作都通过 **Session** 来完成。在 FastAPI 中，通常通过依赖注入来获取 Session。

```python
from sqlalchemy import select
from db import SessionLocal
from models import User

# 获取会话实例
session = SessionLocal()

try:
    # --- 1. 增加 (Create) ---
    new_user = User(username="Alice", age=25)
    session.add(new_user)
    session.commit()   # 提交事务，数据才真正写入数据库
    session.refresh(new_user) # 刷新以获取自增的 ID

    # --- 2. 查询 (Read) ---
    # 查询所有用户
    all_users = session.execute(select(User)).scalars().all()

    # 条件查询：查找用户名为 Alice 的第一个用户
    user = session.execute(select(User).where(User.username == "Alice")).scalars().first()

    # --- 3. 更新 (Update) ---
    if user:
        user.age = 30  # 直接修改对象属性
        session.commit() # 提交修改

    # --- 4. 删除 (Delete) ---
    if user:
        session.delete(user)
        session.commit()

except Exception as e:
    session.rollback() # 发生错误时回滚
    print(f"操作失败: {e}")
finally:
    session.close() # 记得关闭会话
```

---

### 🚀 六、进阶与 FastAPI 结合

#### 1. 异步支持 (AsyncIO)
如果你在使用 FastAPI 构建高性能异步接口，SQLAlchemy 1.4+ 开始提供了完善的 `asyncio` 支持：
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

engine = create_async_engine("mysql+aiomysql://root:123456@localhost/mydb")
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
```

#### 2. 关系映射 (Relationship)
处理表与表之间的关联（如一对多、多对多）：
```python
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class Article(Base):
    __tablename__ = "articles"
    id: Mapped[int] = mapped_column(primary_key=True)
    # 外键
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    # 建立关系，lazy="selectin" 是一种预加载策略，防止 N+1 查询问题
    author: Mapped["User"] = relationship(back_populates="articles", lazy="selectin")

# 在 User 模型中也要加上反向关系
User.articles = relationship("Article", back_populates="author")
```

#### 3. 数据库迁移 (Alembic)
SQLAlchemy 本身不直接管理数据库表结构的变更（比如你加了一个新字段），通常需要配合 **Alembic** 工具来生成和执行迁移脚本。

---

### 💡 七、学习建议

1.  **从 ORM 入手：** 先掌握 `Base`、`Model`、`Session` 的基本用法，能跑通 CRUD。
2.  **理解 Session：** Session 是 ORM 的核心，理解它的生命周期（何时创建、何时提交、何时关闭）非常重要。
3.  **关注 2.0 新特性：** 现在网上的很多教程还是 1.x 版本的写法（比如使用 `session.query(User)`），建议直接学习 2.0 的 `select(User)` 写法，这是未来的标准。
4.  **善用官方文档：** SQLAlchemy 的官方文档非常详尽，遇到报错直接查文档通常能最快解决。

如果你在配置过程中遇到具体的报错（比如之前的 `DeclarativeBase` 问题），随时可以把代码发给我看！

---
要不要我帮你整理一份 SQLAlchemy + FastAPI 的实战模板，可以直接拿去用？
