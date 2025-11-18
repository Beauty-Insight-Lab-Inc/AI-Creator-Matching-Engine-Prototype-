from cryptography.fernet import Fernet

def generate_key():
    """Generates a new encryption key."""
    return Fernet.generate_key()

def encrypt_message(key, message):
    """Encrypts a message using the provided key."""
    f = Fernet(key)
    encrypted_message = f.encrypt(message.encode('utf-8'))
    return encrypted_message

if __name__ == "__main__":
    # 1. Get the database URL from the user
    database_url = input("Please enter your DATABASE_URL to encrypt: ")

    if not database_url:
        print("DATABASE_URL cannot be empty.")
    else:
        # 2. Generate a new encryption key
        key = generate_key()

        # 3. Encrypt the database URL
        encrypted_url = encrypt_message(key, database_url)

        # 4. Print the values to be added to the .env file
        print("\n" + "="*80)
        print("Copy the following lines into your new or existing .env file:")
        print("="*80 + "\n")
        print(f"ENCRYPTION_KEY={key.decode('utf-8')}")
        print(f"ENCRYPTED_DATABASE_URL={encrypted_url.decode('utf-8')}")
        print("\n" + "="*80)
        print("IMPORTANT: Add .env to your .gitignore file to keep your secrets safe!")
        print("="*80)
