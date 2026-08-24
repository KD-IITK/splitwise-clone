from fastapi import FastAPI

from app.modules.users.routes import router as users_router
from app.modules.auth.routes import router as auth_router
from app.modules.groups.routes import router as groups_router
from app.modules.invitations.routes import router as invitations_router

app = FastAPI()


app.include_router(users_router)
app.include_router(auth_router)
app.include_router(groups_router)
app.include_router(invitations_router)

@app.get("/")
def root():
    return {
        "message": "Splitwise Clone API"
    }