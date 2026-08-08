from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from coma2.cocktails.router import router as cocktails_router
from coma2.ingredients.router import router as ingredients_router

app = FastAPI(
    title="coma2",
    description="CocktailMachine V2 backend API",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingredients_router)
app.include_router(cocktails_router)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
