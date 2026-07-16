import hmac
import hashlib
import base64
import json
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FinSwarmCore.Auth")

# In production, this secret key is loaded from secure environment variables (.env)
SECRET_KEY = b"super-secret-finswarm-saas-cryptographic-signing-key-2026"

def base64url_encode(data: bytes) -> str:
    """Encodes bytes to a URL-safe Base64 string without padding."""
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

def base64url_decode(data: str) -> bytes:
    """Decodes a URL-safe Base64 string, adding padding back if necessary."""
    rem = len(data) % 4
    if rem > 0:
        data += '=' * (4 - rem)
    return base64.urlsafe_b64decode(data.encode('utf-8'))

def generate_saas_token(tenant_id: str, company_name: str, expires_in: int = 3600) -> str:
    """
    Generates a cryptographically signed JWT token for a specific tenant workspace.
    """
    # Standard JWT Header specifying the signature algorithm
    header = {"alg": "HS256", "typ": "JWT"}
    
    # Token payload containing claims and tenant properties
    payload = {
        "iss": "finswarm-saas-auth",
        "sub": tenant_id,
        "company": company_name,
        "exp": int(time.time()) + expires_in,
        "iat": int(time.time())
    }
    
    # Base64 encode the header and payload segments
    header_b64 = base64url_encode(json.dumps(header).encode('utf-8'))
    payload_b64 = base64url_encode(json.dumps(payload).encode('utf-8'))
    
    # Generate the HMAC-SHA256 signature
    signing_input = f"{header_b64}.{payload_b64}".encode('utf-8')
    signature = hmac.new(SECRET_KEY, signing_input, hashlib.sha256).digest()
    signature_b64 = base64url_encode(signature)
    
    # Assemble the final token string: header.payload.signature
    return f"{header_b64}.{payload_b64}.{signature_b64}"

def verify_and_decode_token(token: str) -> dict:
    """
    Verifies the cryptographic signature of a JWT and returns the claims payload.
    Raises ValueError if the signature is invalid or the token is expired.
    """
    try:
        parts = token.split('.')
        if len(parts) != 3:
            raise ValueError("Malformed token structure.")
            
        header_b64, payload_b64, signature_b64 = parts
        
        # Verify signature integrity
        signing_input = f"{header_b64}.{payload_b64}".encode('utf-8')
        expected_sig = hmac.new(SECRET_KEY, signing_input, hashlib.sha256).digest()
        actual_sig = base64url_decode(signature_b64)
        
        if not hmac.compare_digest(expected_sig, actual_sig):
            raise ValueError("Cryptographic signature verification failed. Token is untrusted.")
            
        # Decode and parse payload claims
        payload = json.loads(base64url_decode(payload_b64).decode('utf-8'))
        
        # Check token expiration
        if time.time() > payload.get("exp", 0):
            raise ValueError("Access token has expired.")
            
        return payload
    except Exception as e:
        logger.error(f"Token validation rejection: {str(e)}")
        raise ValueError(f"Authentication invalid: {str(e)}")