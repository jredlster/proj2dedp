from werkzeug.security import generate_password_hash

new_hash = generate_password_hash("Admin@123!", method="pbkdf2:sha256:150000")
print(new_hash)