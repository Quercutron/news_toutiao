from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

#数据库url
ASYNC_DATABASE_URL = "mysql+aiomysql://root:root@localhost:3306/news_app?charset=utf8mb4"
#创建异步引擎
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,#输出日志
    pool_size=10,#连接池大小
    max_overflow=20,#连接池最大溢出数
)

#创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,#绑定引擎
    class_=AsyncSession,#会话类
    expire_on_commit=False,#提交后过期
)

#创建依赖项，用于获取数据库会话
async def create_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
