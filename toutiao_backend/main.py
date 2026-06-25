import uvicorn
from fastapi import FastAPI
from routers import news, users, favorite, history
from fastapi.middleware.cors import CORSMiddleware
from utils.exception_handle import register_exception_handlers
app = FastAPI()

# 注册全局异常处理器
register_exception_handlers(app)

origins = [
    "http://localhost:5173",
    "http://localhost:8080",
    "https://your-frontend-domain.com",
    "http://127.0.0.1:8080"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}


#挂载路由，注册路由
app.include_router(news.router)
app.include_router(users.router)
app.include_router(favorite.router)
app.include_router(history.router)



if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)