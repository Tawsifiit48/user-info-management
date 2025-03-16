import psycopg2
from psycopg2 import pool
import threading
import queue

from utils.logger_config import setup_logger

logger = setup_logger('connection')

MAX_CONN = 5

connPool = None
connQueue = queue.Queue(maxsize=MAX_CONN)
mutex = threading.Lock()

def init_pool(conninfo):
    print("Initializing connection pool...")
    global connPool
    with mutex:
        connPool = psycopg2.pool.SimpleConnectionPool(
            1, MAX_CONN, conninfo
        )
        if connPool:
            logger.info(f"Connection pool initialized with {MAX_CONN} connections.")
        else:
            print("Failed to initialize connection pool.")

        # Add connections to the queue
        for _ in range(MAX_CONN):
            conn = connPool.getconn()
            connQueue.put(conn)
            print(f"Connection added to queue. Queue size: {connQueue.qsize()}")

def get_connection():
    with mutex:
        if connQueue.qsize() > 0:
            conn = connQueue.get()
            print(f"Connection retrieved from queue. Queue size: {connQueue.qsize()}")
            return conn
        else:
            print("No available connections in queue.")
            return None

def release_connection(conn):
    with mutex:
        connQueue.put(conn)
        print(f"Connection returned to queue. Queue size: {connQueue.qsize()}")
