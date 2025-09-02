KnowYourCampus API Documentation

This document outlines the API endpoints for the KnowYourCampus application.

Base URL: http://0.0.0.0:8000

Authentication Flow

    A new user signs up using the POST /api/v1/users/signup endpoint.

    The client app receives and securely stores the user_id.

    The user logs in using POST /api/v1/auth/login to re-verify credentials and get their user_id.

    The stored user_id is used in the URL for subsequent API calls that require it.

API v1 Endpoints (Core User & Auth)

Sign-Up New User

    Endpoint: POST /api/v1/users/signup

    Description: Registers a new user.

    Request Body:
    JSON

{ "email": "user@example.com", "password": "a_strong_password" }

Success Response (200 OK):
JSON

    { "is_valid": true, "user_id": "..." }

Log In User

    Endpoint: POST /api/v1/auth/login

    Description: Authenticates an existing user.

    Request Body:
    JSON

{ "email": "user@example.com", "password": "the_correct_password" }

Success Response (200 OK):
JSON

    { "is_valid": true, "user_id": "..." }

Get User Profile

    Endpoint: GET /api/v1/users/{user_id}/profile

    Description: Fetches public profile details for a given user.

    Success Response (200 OK):
    JSON

    {
      "university_reg_no": "4SO22CS001",
      "biography": "Computer Science student.",
      "interest1": "AI",
      "interest2": "Web Dev",
      "interest3": "Databases"
    }

API v2 Endpoints (Profiles, Matching & Connections)

Set Up User Profile

    Endpoint: PUT /api/v1/users/{user_id}/setup

    Description: Sets or updates a user's profile details and interests.

    Request Body:
    JSON

    {
      "name": "Alex Smith",
      "university_reg_no": "4SO22CS001",
      "biography": "Computer Science student.",
      "interest1": "AI", "interest1_weight": 8,
      "interest2": "Web Dev", "interest2_weight": 6,
      "interest3": "Databases", "interest3_weight": 5
    }

Generate User Matches

    Endpoint: POST /api/v2/algo/match/{user_id}

    Description: Triggers the matching algorithm and returns the top 10 matches.

    Success Response (200 OK):
    JSON

    { "matches": ["uuid-1", "uuid-2", "..."] }

Send Connection Request

    Endpoint: POST /api/v2/connections/request

    Path Parameter in URL: user_id of the sender.

    Request Body:
    JSON

{ "addressee_id": "user-id-to-connect-with" }

Success Response (201 Created):
JSON

    { "message": "Connection request has been sent to 4SO22CS001" }

View Pending Requests

    Endpoint: GET /api/v2/connections/{user_id}/requests/pending

    Description: Gets a list of users who have sent a connection request to you.

    Success Response (200 OK):
    JSON

    [
      {
        "requester_id": "...",
        "university_reg_no": "4SO22CS002",
        "biography": "...", "interest1": "...", "interest2": "...", "interest3": "..."
      }
    ]

Respond to Request

    Endpoint: PUT /api/v2/connections/{user_id}/requests/respond

    Description: Accept or decline a pending request. user_id is your ID.

    Request Body:
    JSON

    { "requester_id": "user-id-who-sent-the-request", "new_status": "accepted" }

    Success Response: 204 No Content

View Friends

    Endpoint: GET /api/v2/connections/{user_id}/friends

    Description: Gets a list of USNs for all accepted connections.

    Success Response (200 OK):
    JSON

    { "usns": ["4SO22CS002", "4SO22CS003"] }

API v3 Endpoints (Real-Time Messaging)

Get Chat History

    Endpoint: GET /api/v3/messages/{user_id}/conversation/{other_user_id}

    Description: Retrieves the full chat history between two users.

    Success Response (200 OK):
    JSON

    [
      { "id": 1, "sender_id": "...", "receiver_id": "...", "content": "Hello!", "timestamp": "..." }
    ]

Get Video Call Link

    Endpoint: GET /api/v3/messages/{user_id}/meet/{other_user_id}

    Description: Generates a unique Google Meet link for a video call.

    Success Response (200 OK):
    JSON

    { "meet_link": "https://meet.google.com/lookup/..." }

Real-Time WebSocket Connection

To engage in real-time chat, the client must open and maintain a persistent WebSocket connection.

    URL: ws://<your_server_address>/api/v3/messages/ws/{user_id}

    Path Parameter:

        user_id (UUID string): The unique ID of the user who is connecting.

    Sending Messages: To send a message, the client must send a JSON object through the open WebSocket with the following structure:
    JSON

{
  "receiver_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
  "content": "Hello! How are you?"
}

Receiving Messages: The client should listen on the WebSocket for incoming JSON messages, which will have the full MessageResponse structure.