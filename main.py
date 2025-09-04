from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from db.session import engine
from db.base import Base
from api.api_v1 import api_router
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import sys
import traceback
from dotenv import load_dotenv
from api.api_v1 import api_router
from api.endpoints import items, users
from config import HOST, PORT, USE_HTTPS, SSL_CERT_FILE, SSL_KEY_FILE, STATIC_DIR

# 加载环境变量
load_dotenv()

def create_tables():
    Base.metadata.create_all(bind=engine)

def include_router(app):
    app.include_router(api_router, prefix="/api/v1")

def start_application():
    app = FastAPI(title="二手交易系统", version="1.0.0", debug=True)
    # create_tables()  # Only run this manually during development or use Alembic for migrations
    include_router(app)
    return app

app = start_application()

# 添加全局异常中间件
@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        print("全局异常捕获：", e)
        traceback.print_exc(file=sys.stdout)
        raise e

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 或指定你的前端地址如 ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    """
    Root endpoint that confirms the 二手交易系统 is running.
    """
    return {"message": "二手交易系统 is running"}

# 获取当前文件所在目录的绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print(f"项目根目录: {BASE_DIR}")
print(f"静态文件目录: {STATIC_DIR}")

# 挂载静态文件
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# 添加测试路由
@app.get("/test-static")
async def test_static():
    test_file_path = os.path.join(STATIC_DIR, "images", "test.txt")
    
    # 创建测试文件
    with open(test_file_path, "w") as f:
        f.write("静态文件服务测试 - 成功!")
    
    return {
        "static_dir": str(STATIC_DIR),
        "test_file_path": test_file_path,
        "test_file_url": "/static/images/test.txt"
    }

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # 记录错误但不返回不可序列化的 body
    print(f"验证错误: {exc.errors()}")
    
    # 清理错误信息，移除不可序列化的内容
    clean_errors = []
    for error in exc.errors():
        clean_error = {
            "type": error.get("type"),
            "loc": error.get("loc"),
            "msg": error.get("msg"),
            "input": str(error.get("input")) if error.get("input") is not None else None
        }
        clean_errors.append(clean_error)
    
    return JSONResponse(
        status_code=422,
        content={"detail": clean_errors},
    )

# 添加启动服务器的代码
if __name__ == "__main__":
    import uvicorn
    print("正在启动 Uvicorn 服务器...")
    
    if USE_HTTPS and SSL_CERT_FILE.exists() and SSL_KEY_FILE.exists():
        print("使用HTTPS模式启动...")
        uvicorn.run(
            "main:app", 
            host=HOST, 
            port=PORT, 
            reload=True,
            ssl_certfile=str(SSL_CERT_FILE),
            ssl_keyfile=str(SSL_KEY_FILE)
        )
    else:
        print("使用HTTP模式启动...")
        uvicorn.run("main:app", host=HOST, port=PORT, reload=True)