import bcrypt
import secrets

def hash_password(password: str) -> str:
    """Hashes a password using bcrypt and returns a string."""
    # bcrypt requires bytes, so we encode the string to utf-8 first
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(pwd_bytes, salt)
    
    # Return as a regular string to store in Postgres
    return hashed_bytes.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain text password against the hashed version from the DB."""
    plain_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    
    return bcrypt.checkpw(plain_bytes, hashed_bytes)

def generate_license_key() -> str:
    """generates license key for bot."""
    return secrets.token_hex(16)  