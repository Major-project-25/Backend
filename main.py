# main.py

from fastapi import FastAPI
from api.v1 import routes_users, routes_auth
from api.v2 import routes_algo, routes_connections

app = FastAPI(title="KnowYourCampus API")

# --- Version 1 Endpoints (Stable) ---
app.include_router(routes_users.router, prefix="/api/v1/users", tags=["Users (v1)"])
app.include_router(routes_auth.router, prefix="/api/v1/auth", tags=["Auth (v1)"])

# --- Version 2 Endpoints (New Features) ---
app.include_router(routes_algo.router, prefix="/api/v2/algo", tags=["Algorithms (v2)"])
app.include_router(routes_connections.router, prefix="/api/v2/connections", tags=["Connections (v2)"])