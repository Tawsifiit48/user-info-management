from connection import get_connection, release_connection
from psycopg2.extras import execute_values
import time
import hashlib
import os
from utils.logger_config import setup_logger

logger = setup_logger('query')

def create_user(first_name, last_name, password, phone):
    conn = get_connection()
 
    try:
        logger.info(f"Creating user with first name: {first_name}, last name: {last_name}, phone: {phone}")
        salt = os.urandom(16)  
        password_salt_combined = password.encode('utf-8') + salt
        hashed_password = hashlib.sha256(password_salt_combined).hexdigest()
        if not conn:
            logger.error("Failed to connect to database for creating user")
            return False
        
        cur = conn.cursor()

        insert_query = """
            INSERT INTO users (firstName, lastName, password, phone, salt)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (phone) 
            DO UPDATE 
            SET firstName = EXCLUDED.firstName,
                lastName = EXCLUDED.lastName,
                password = EXCLUDED.password,
                salt = EXCLUDED.salt
            RETURNING userId;
        """

        cur.execute(insert_query, (first_name, last_name, hashed_password, phone, salt))
        result = cur.fetchone()

        if result:
            user_id = result[0]
            conn.commit()
            release_connection(conn)
            logger.info(f"User created successfully with userId: {user_id}")
            return user_id
        else:
            logger.error("Error: No userId returned from the query.")
            release_connection(conn)
            return False

    except Exception as e:
        release_connection(conn)
        logger.error(f"Error occurred while creating user: {e}")
        return False

def get_user_by_id(user_id):
    conn = get_connection()

    try:
        logger.info(f"Fetching user with userId: {user_id}")
        
        if not conn:
            logger.info("Failed to connect to database for fetching user")
            return None
        
        cur = conn.cursor()

        query = "SELECT userId, firstName, lastName, phone FROM users WHERE userId = %s;"
        cur.execute(query, (user_id,))
        
        result = cur.fetchone()
        cur.close()
        release_connection(conn)
        
        if result:
            user_data = {
                "userId": result[0],
                "firstName": result[1],
                "lastName": result[2],
                "phone": result[3]
            }
            return user_data
        else:
            logger.error(f"Error: No user found with userId: {user_id}")
            release_connection(conn)
            return {"error": "User not found"}
    except Exception as e:
        release_connection(conn)
        logger.error(f"Error occurred while fetching user: {e}")
        
        return {"error": "Internal server error"}


def add_tags_db(user_id, tags, expiry):
    
    conn = get_connection()

    try:
        logger.info(f"Adding/updating tags for userId: {user_id}, tags: {tags}, expiry: {expiry}")
        batch_size = 1000
        with conn.cursor() as cursor:
            for i in range(0, len(tags), batch_size):
                batch = tags[i: i + batch_size]
                values = [(user_id, tag, expiry) for tag in batch]

                insert_query = """
                    INSERT INTO user_tags (user_id, tag, expiry) 
                    VALUES %s
                    ON CONFLICT (user_id, tag) 
                    DO UPDATE SET expiry = EXCLUDED.expiry;
                """
                execute_values(cursor, insert_query, values)
            conn.commit()


        release_connection(conn)
        return True
    except Exception as e:
        logger.error(f"Error inserting/updating tags: {e}")
        conn.rollback()
        release_connection(conn)
        return False

def get_users_by_tags_from_db(tags):
    conn = get_connection()

    try:

        logger.info(f"Fetching users with tags: {tags}")
        with conn.cursor() as cursor:
            query = """
                SELECT u.userid, u.firstname  || ' ' || u.lastname  AS name, array_agg(ut.tag) AS tags
                FROM users u
                JOIN user_tags ut ON u.userid = ut.user_id
                WHERE ut.tag = ANY(%s)
                GROUP BY u.userid;

            """
            print(query)
            cursor.execute(query, (tags,))
            users = cursor.fetchall()
            release_connection(conn)

        return [
            {"id": user[0], "name": user[1], "tags": user[2]}
            for user in users
        ]
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        release_connection(conn)
        return []


def cleanup_expired_tags_from_db():
    while True:
        conn = get_connection()
        if not conn:
            logger.info("Error: Database connection pool is not initialized.")
            time.sleep(10)
            continue
        try:
            with conn.cursor() as cursor:
                query = "DELETE FROM user_tags WHERE expiry < EXTRACT(EPOCH FROM NOW()) * 1000;"
                cursor.execute(query)
                deleted_count = cursor.rowcount
                conn.commit()
                release_connection(conn)
                logger.info(f"Expired tags deleted: {deleted_count} rows removed.")
        except Exception as e:
            logger.error(f"Error deleting expired tags: {e}")
            release_connection(conn)

        time.sleep(600) 