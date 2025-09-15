from schema.connections import PendingRequestDetail, FriendsResponse, FriendDetail

# --- THIS IS THE FIXED ENDPOINT ---
@router.get("/{user_id}/friends", response_model=FriendsResponse)
def view_all_accepted_connections(user_id: UUID, db: Session = Depends(get_db)):
    """ 4. Viewing All Accepted Connections (Friends) """
    connections = connection_services.view_friends(db, user_id=user_id)
    
    friends_list = []
    for conn in connections:
        # Determine who the "other person" in the connection is
        other_person = conn.addressee if conn.requester_id == user_id else conn.requester
        
        # Create a detailed object for each friend
        friends_list.append(
            FriendDetail(
                user_id=other_person.id,
                university_reg_no=other_person.university_reg_no,
                name=other_person.name
            )
        )
        
    return {"friends": friends_list}
