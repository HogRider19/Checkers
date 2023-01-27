from dotenv import load_dotenv
import os


load_dotenv()

DB_USER = os.getenv('db_user', 'postgres')
DB_PASSWORD = os.getenv('db_password', 'postgres')
DB_HOST = os.getenv('db_host')
DB_PORT = os.getenv('db_port', '')
DB_NAME = os.getenv('db_name', 'postgres')
DB_DRIVER = os.getenv('db_driver', 'psycopg2')

SECRET = os.getenv('secret')

TESTING_DB_NAME = os.getenv('testing_db_name', 'testing_db')

DB_PORT = f":{DB_PORT}" if DB_PORT and DB_PORT[0] != ':' else DB_PORT