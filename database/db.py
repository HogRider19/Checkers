import databases
import sqlalchemy

from config.config import (DB_DRIVER, DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT,
                           DB_USER)


DATABASEURL = f"postgresql+{DB_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}{DB_PORT}/{DB_NAME}"

database = databases.Database(DATABASEURL)
metadata = sqlalchemy.MetaData()