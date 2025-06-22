from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from db.session import engine
from db.base import Base
from api.api_v1 import api_router
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os
from api.api_v1 import api_router
from api.endpoints import items, users

def create_tables():
    Base.metadata.create_all(bind=engine)

def include_router(app):
    app.include_router(api_router, prefix="/api/v1")

def start_application():
    app = FastAPI(title="Goofish API", version="1.0.0")
    # create_tables()  # Only run this manually during development or use Alembic for migrations
    include_router(app)
    return app

app = start_application()

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    """
    Root endpoint that confirms the Goofish API is running.
    """
    return {"message": "Goofish API is running"}

# 获取当前文件所在目录的绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")# 获取当前文件所在目录的绝对路径
print(f"项目根目录: {BASE_DIR}")
print(f"静态文件目录: {STATIC_DIR}")
# 配置静态文件服务
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
# 添加测试路由
@app.get("/test-static")
async def test_static():
    test_file_path = os.path.join(STATIC_DIR, "images", "test.txt")
    
    # 创建测试文件
    with open(test_file_path, "w") as f:
        f.write("静态文件服务测试 - 成功!")
    
    return {
        "static_dir": STATIC_DIR,
        "test_file_path": test_file_path,
        "test_file_url": "/static/images/test.txt"
    }

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # 记录错误但不返回不可序列化的 body
    print(f"验证错误: {exc.errors()}")
    
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )
# 添加CORS中间件，允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # 关键：允许暴露 Content-Type 头
    expose_headers=["Content-Type", "Content-Disposition"]
)

# 添加启动服务器的代码
if __name__ == "__main__":
    import uvicorn
    print("正在启动 Uvicorn 服务器...")
    # 注意：为了让reload生效，app必须以字符串形式传入
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)