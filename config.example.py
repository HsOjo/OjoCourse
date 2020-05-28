COURSE_HOST = ''
COURSE_PROTOCOL = 'http'
COURSE_SYNC_INTERVAL = 86400
# Basic Auth
COURSE_AUTH = None
# COURSE_AUTH=('<username>', '<password>')

EDU_ADMIN_HOST = ''
EDU_ADMIN_PROTOCOL = 'http'
# Basic Auth
EDU_ADMIN_AUTH = None
# EDU_ADMIN_AUTH=('<username>', '<password>')


DB_HOST = '127.0.0.1'
DB_PORT = 3306
DB_USER = 'root'
DB_PASSWORD = ''
DB_DATABASE = ''
DB_CHARSET = 'utf8mb4'

SECRET_KEY = 'OjoCourse'
DATA_DIR = './data'

COURSE_CONFIG = dict(
    host=COURSE_HOST, auth=COURSE_AUTH, protocol=COURSE_PROTOCOL
)

EDU_ADMIN_CONFIG = dict(
    host=EDU_ADMIN_HOST, auth=EDU_ADMIN_AUTH, protocol=EDU_ADMIN_PROTOCOL
)

SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://%s:%s@%s:%d/%s?charset=%s' % (
    DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_DATABASE, DB_CHARSET
)
