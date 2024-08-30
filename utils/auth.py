# auth.py

roles = {
    'Person': ['trey.hulse@kcstorefixtures.co', 'treyhulse3@gmail.co', 'user1@example.com'],
    'Manager': ['trey.hulse@kcstorefixtures.co', 'treyhulse3@gmail.co', 'user2@example.com'],
    'Director': ['trey.hulse@kcstorefixtures.com', 'treyhulse3@gmail.com', 'user3@example.com'],
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
