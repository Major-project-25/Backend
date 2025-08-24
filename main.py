from fastapi import FastAPI
from api.v1 import routes_users

app = FastAPI(title="KnowYourCampus API", version="1.0.0")

# Register routers
app.include_router(routes_users.router, prefix="/api/v1/users", tags=["Users"])
#app.include_router(routes_auth.router, prefix="/api/v1/auth", tags=["Auth"])
#app.include_router(routes_algo.router, prefix="/api/v1/algo", tags=["Algo"])
