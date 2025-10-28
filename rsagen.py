from Crypto.PublicKey import RSA
import os

def generate_keys(key_size=5000, keys_dir="keys"):
    """
    Generates and saves RSA public and private keys.

    Args:
        key_size (int): The size of the key to generate.
        keys_dir (str): The directory to save the keys in.

    Returns:
        tuple: A tuple containing the paths to the private and public keys.
    """
    if not os.path.exists(keys_dir):
        os.makedirs(keys_dir)
        print(f"Created directory: {keys_dir}")

    private_key_path = os.path.join(keys_dir, f"private_key_{key_size}.pem")
    public_key_path = os.path.join(keys_dir, f"public_key_{key_size}.pem")

    # Check if keys already exist
    if os.path.isfile(private_key_path) and os.path.isfile(public_key_path):
        print("RSA keys already exist.")
        return private_key_path, public_key_path

    # Generate a new key pair
    key_pair = RSA.generate(key_size)

    # Save the private key
    with open(private_key_path, "wb") as f:
        f.write(key_pair.exportKey('PEM'))

    # Save the public key
    pubkey = key_pair.publickey()
    with open(public_key_path, "wb") as f:
        f.write(pubkey.exportKey('OpenSSH'))

    print(f"Public and private keys have been created and stored in '{keys_dir}'.")
    return private_key_path, public_key_path

if __name__ == '__main__':
    generate_keys()
