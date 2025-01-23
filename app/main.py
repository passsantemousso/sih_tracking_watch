from fastapi import FastAPI, HTTPException
from app.api.devices import router as devices_router

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Bienvenue sur l'API FastAPI pour MongoDB!"}

# Inclure les routes de l'API
app.include_router(devices_router, prefix="/devices", tags=["devices"])
# app.include_router(users_router, prefix="/users", tags=["users"])





