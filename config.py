import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret-key'

    BLOB_ACCOUNT = 'storagejaredcms'
    BLOB_CONTAINER = 'images'
    BLOB_STORAGE_KEY = os.environ.get('BLOB_STORAGE_KEY')

    SQL_SERVER = 'cms-jared.database.windows.net'
    SQL_DATABASE = 'cms-jareddb'
    SQL_USER_NAME = "cms-admin@cms-jared"
    SQL_PASSWORD = 'jared123!'

    SQLALCHEMY_DATABASE_URI = (
        f"mssql+pyodbc://{SQL_USER_NAME}:{SQL_PASSWORD}"
        f"@{SQL_SERVER}:1433/{SQL_DATABASE}"
        "?driver=ODBC+Driver+17+for+SQL+Server"
        "&Encrypt=yes"
        "&TrustServerCertificate=no"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CLIENT_ID = "0e4b2d48-600f-4bde-9c9d-cad31d8c84f3"
    CLIENT_SECRET = os.environ.get("CLIENT_SECRET")

    AUTHORITY = "https://login.microsoftonline.com/common"
    REDIRECT_PATH = "/getAToken"
    REDIRECT_URI = "http://localhost:5000/getAToken"

    SCOPE = ["User.Read"]
    SESSION_TYPE = "filesystem"
