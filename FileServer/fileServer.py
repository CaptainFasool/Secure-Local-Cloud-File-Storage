import socket
import ssl
import os
import pyotp
import qrcode
from argon2 import PasswordHasher

# Configure server socket, bind to (IP, port) and listen for incoming connection
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('localhost', 6969))
server.listen(1)

# Create an SSL context configured for secure server-side TLS communications
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile="server.crt", keyfile="server.key") # Loads cert file to send to client during communication and private key to decrypt data

# Set the correct password's (argon2) hash
correct_password = os.getenv("PASSWD")
client, addr = server.accept()
client = context.wrap_socket(client, server_side=True) # Wrap the server socket with TLS
client.settimeout(60)

# Send initial prompt for password
client.send(b"Please enter password: ")

# Verify password with argon2 algo
ph = PasswordHasher()
password_attempt = client.recv(1024).decode("utf-8").strip()
try: # a match causes argon2 to return None and continue silently
    password_check = ph.verify(correct_password, password_attempt)
except: # a mismatch causes argon2 to raise an exception, so we terminate the session in that case.
    client.send(b"Incorrect password. Connection terminated.")
    client.close()
    server.close()
    exit()

secret = pyotp.random_base32()
totp = pyotp.TOTP(secret)
uri = totp.provisioning_uri(name="faisal@filecloud", issuer_name="LocalFileCloud")

# Send the URI to the client so it can render its own QR
client.send(uri.encode("utf-8"))
otp_input = client.recv(1024).decode("utf-8").strip()
if totp.verify(otp_input) == False:  # Fixed: changed otp to totp
    client.send(b"Invalid OTP. Connection terminated.")
    client.close()
    server.close()
    exit()

# Password is correct, proceed with normal operation
client.send(b"Welcome to your local file cloud. Start by adding some .txt files or retrieving them (r/w). ")
while True:
    try:
        option = client.recv(1024).decode("utf-8").strip()
        if option.lower() == 'w':
            client.send(b"Enter filename to upload (e.g., hello.txt): ")
            fileName = client.recv(1024).decode("utf-8").strip()
            
            if ".txt" not in fileName:
                client.send(b"Invalid file format.")
                continue
            else:
                client.send(b"Transferring file...")
                with open(fileName, 'w') as txtFile:
                    while True:
                        fileContent = client.recv(1024).decode("utf-8")
                        if not fileContent or "<<END_OF_FILE>>" in fileContent:
                            if "<<END_OF_FILE>>" in fileContent:
                                # Remove the marker and write remaining content
                                txtFile.write(fileContent.replace("<<END_OF_FILE>>", ""))
                            break # Break out of loop after all file contents are transferred and fileContent becomes empty
                        txtFile.write(fileContent)
                client.send(b"Transfer complete!")
                continue
        elif option.lower() == 'r':
            with open('hello.txt', 'r') as txtFile:
                fileContent = txtFile.read()
            client.send(fileContent.encode("utf-8"))
            continue
        else:
            client.send(b"Invalid option.")
            continue
    except socket.timeout:
        print("Session timed out.")
        break

server.close()