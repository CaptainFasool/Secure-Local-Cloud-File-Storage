import socket
import ssl
import qrcode

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Configure SSL/TLS context
context = ssl.create_default_context()
context.minimum_version = ssl.TLSVersion.TLSv1_2  # Force strong TLS 1.2 or higher
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE # self-signed certs don't require verification
client = context.wrap_socket(client, server_hostname='localhost') # disable cert verification for local use/testing
client.connect(('localhost', 6969))

# Handle password request
message = client.recv(1024).decode("utf-8")
print(message, end="")  # Print password prompt
password = input()
client.send(password.encode("utf-8"))

# If password was incorrect, the message will say so and we should exit
response = client.recv(1024).decode("utf-8")
if "Incorrect password" in response:
    print(response)
    client.close()
    exit()

# Receive URI
uri = response

# Create and print QR in terminal
qr = qrcode.QRCode()
qr.add_data(uri)
qr.make()
qr.print_ascii(invert=True)  # Invert to make it scannable on dark terminals
otp = input("Scan the QR code with an authenticator app and enter the OTP: ")
client.send(otp.encode("utf-8"))

# Receive OTP verification response and welcome message
message = client.recv(1024).decode("utf-8")
print(message)
if "Invalid OTP" in message:
    client.close()
    exit()

# Continue with normal operation
while True:
    option = input("Enter option (r to read/w to write/q to quit): ")
    client.send(option.encode("utf-8"))
    if option.lower() == 'w':
        response = client.recv(1024).decode("utf-8")
        print(response)
        fileName = input()
        client.send(fileName.encode("utf-8"))
        message = client.recv(1024).decode("utf-8")
        print(message)
        if "Invalid file format" in message:
            continue
        with open(fileName, 'r') as file:
            fileContent = file.read()
            client.send((fileContent + "<<END_OF_FILE>>").encode("utf-8"))
        
        # After sending file, receive confirmation
        message = client.recv(1024).decode('utf-8')
        print(message)
    elif option.lower() == 'r':
        message = client.recv(1024).decode("utf-8")
        print(message)
    elif option.lower() == 'q':
        client.close()
        exit()
    else:
        message = client.recv(1024).decode("utf-8")
        print(message)

client.close()