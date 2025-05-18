from passlib.context import CryptContext

# singleton
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class PasswordHasher():
    
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)
         
    @staticmethod
    def verify_password(input_password: str, hash_password: str) -> bool:
        return pwd_context.verify(input_password, hash_password)
    