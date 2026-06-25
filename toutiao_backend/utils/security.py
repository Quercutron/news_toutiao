#passlib数据加密
# 创建密码加密上下文
# from passlib.context import CryptContext
#
# pwd_context = CryptContext(
#      schemes=["bcrypt"],
#      deprecated="auto"
# )
# # 加密
# def get_password_hash(password: str) -> str:
#     # 对密码进行加密
#     password = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
#     return pwd_context.hash(password)
#
# # 密码校验
# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     # 验证密码
#     plain_password = plain_password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
#     return pwd_context.verify(plain_password, hashed_password)



# Deleted:#passlib数据加密
# Deleted:# 创建密码加密上下文
# Deleted:from passlib.context import CryptContext
# Deleted:
# Deleted:pwd_context = CryptContext(
# Deleted:     schemes=["bcrypt"],
# Deleted:     deprecated="auto"
# Deleted:)
import bcrypt

# 加密
def get_password_hash(password: str) -> str:
    password_bytes = password.encode('utf-8')[:72]
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode('utf-8')

# 密码校验
def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode('utf-8')[:72]
    return bcrypt.checkpw(password_bytes, hashed_password.encode('utf-8'))
