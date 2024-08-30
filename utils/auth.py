# auth.py

roles = {
    'Person': ['trey.huls@kcstorefixtures.com', 'person2@example.com', 'user1@example.com'],
    'Manager': ['trey.huls@kcstorefixtures.com', 'manager2@example.com', 'user2@example.com'],
    'Director': ['trey.hulse@kcstorefixtures.com', 'director2@example.com', 'user3@example.com'],
}

def has_role(email, role):
    return email in roles.get(role, [])

def has_any_role(email, role_list):
    return any(has_role(email, role) for role in role_list)

def get_user_role(email):
    for role, emails in roles.items():
        if email in emails:
            return role
    return None
