# main.py

from fastapi import FastAPI
from api.v1 import routes_users, routes_auth
from api.v2 import routes_algo, routes_connections
from api.v3 import routes_msg
from api.v4 import routes_admin, routes_posts
from fastapi.staticfiles import StaticFiles
import os

# --- THIS SECTION IS UPDATED FOR ROBUST PATHS ---
# Get the absolute path to the directory where main.py is located
# For example: /home/pi/Documents/knowyourcampus/Backend
SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

# Create a full, absolute path for the static directory
# For example: /home/pi/Documents/knowyourcampus/Backend/static
STATIC_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, "static")

# Create a full, absolute path for the uploads subdirectory
UPLOADS_DIRECTORY = os.path.join(STATIC_DIRECTORY, "uploads")
# -----------------------------------------------------------

app = FastAPI(title="KnowyourCampus API")

# Create the directories using the absolute path
os.makedirs(UPLOADS_DIRECTORY, exist_ok=True)

# Mount the static directory using the absolute path
app.mount("/static", StaticFiles(directory=STATIC_DIRECTORY), name="static")


# --- Version 1 Endpoints (Login) ---
app.include_router(routes_users.router, prefix="/api/v1/users", tags=["Users (v1)"])
app.include_router(routes_auth.router, prefix="/api/v1/auth", tags=["Auth (v1)"])

# --- Version 2 Endpoints (Connections) ---
app.include_router(routes_algo.router, prefix="/api/v2/algo", tags=["Algorithms (v2)"])
app.include_router(routes_connections.router, prefix="/api/v2/connections", tags=["Connections (v2)"])

# --- Version 3 Endpoints (Messaging) ---
app.include_router(routes_msg.router, prefix="/api/v3/messages", tags=["Messaging (v3)"])

# --- Version 4 Endpoints (Admin) - --
app.include_router(routes_admin.router, prefix="/api/v4/admin", tags=["Admin (v4)"])
app.include_router(routes_posts.router, prefix="/api/v4/posts", tags=["Posts (v4)"])

