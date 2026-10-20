from passlib.context import  CryptContext

#创建密码的上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hash_password(password:str):
    """
    密码加密功能的函数
    """

    return  pwd_context.hash(password)
def verify_password(plain_password, hashed_password):
    """
    验证密码
    """
    return pwd_context.verify(plain_password, hashed_password)
