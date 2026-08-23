from fastapi import FastAPI

from app.modules.users.routes import router as users_router
from app.modules.auth.routes import router as auth_router

app = FastAPI()


app.include_router(users_router)
app.include_router(auth_router)

@app.get("/")
def root():
    return {
        "message": "Splitwise Clone API"
    }