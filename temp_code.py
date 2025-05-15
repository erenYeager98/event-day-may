import base64
encoded_str = "aHR0cDovLzU0LjE5Ny4xNi4xNjMvdGVybWluYWw="

# Decode it
decoded_bytes = base64.b64decode(encoded_str)
decoded_str = decoded_bytes.decode('utf-8')

print("Secret:", decoded_str)

