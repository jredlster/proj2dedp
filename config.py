import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret-key'

    BLOB_ACCOUNT = 'storagejaredcms'
    BLOB_CONTAINER = 'images'
    BLOB_STORAGE_KEY = 'wIJtJVrgROYCut31QFIuTIauelCu+UrgWfUnPLZlVBwSD+CPbmdbN5x9H2MyTPgHXo7rgt5ladh8+AStkYZYDg=='

    SQL_SERVER = 'cms-jared.database.windows.net'
    SQL_DATABASE = 'cms-jareddb'
    SQL_USER_NAME = "cms-admin"
    SQL_PASSWORD = 'jared123!'

    SQLALCHEMY_DATABASE_URI = (
        f"mssql+pyodbc://{SQL_USER_NAME}:{SQL_PASSWORD}"
        f"@{SQL_SERVER}:1433/{SQL_DATABASE}"
        
        "?driver=ODBC+Driver+17+for+SQL+Server"
        "&Encrypt=yes"
        "&TrustServerCertificate=no"

    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CLIENT_ID = "81a31aea-4f6a-4e6d-bfe5-8a0004630f64"
    CLIENT_SECRET = 'OSg8Q~rJDCL_uIUnNT-7SgfPAXtkNUR8tK5fOc6a'

    AUTHORITY = "https://login.microsoftonline.com/common"
    REDIRECT_PATH = "/getAToken"
    REDIRECT_URI = "http://localhost:5000/getAToken"
    #REDIRECT_URI = os.environ.get("REDIRECT_URI") or "http://localhost:5000/getAToken"

    SCOPE = ["User.Read"]
    SESSION_TYPE = "filesystem"
