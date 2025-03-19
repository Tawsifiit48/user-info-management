def check_health():
    return "I am alive"

def add_user(firstName, lastName, password, phone):
    from query import create_user 
    return create_user(firstName, lastName, password, phone)

def add_tags(user_id, tags, expiry):
    from query import add_tags_db
    return add_tags_db(user_id, tags, expiry)

def get_users_by_tags(tags):
    from query import get_users_by_tags_from_db
    return get_users_by_tags_from_db(tags)

def cleanup_expired_tags():
    from query import cleanup_expired_tags_from_db
    return cleanup_expired_tags_from_db()