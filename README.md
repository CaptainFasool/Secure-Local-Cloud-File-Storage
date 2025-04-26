# Secure-Local-Cloud-File-Storage

This is a limited release of my local cloud file storage system, which currently only works with .txt files.

The system leverages Python sockets secured with TLS to establish encrypted communication between the server and client. The TLS-wrapped sockets open a secure session between endpoints. The digital certificate is not verified, as a self-signed certificate was used for local development and testing purposes. For real-world deployment, the server's digital certificate must be signed by a trusted Certificate Authority (CA) to ensure authenticity.

The digital certificate allows the client to verify the server's identity with the public key, while the embedded digital signature ensures the integrity of the communication.

For added security, MFA/2FA was implemented, prompting user authentication with a password (something they know) and a TOTP (something they have). The password is hashed with argon2, a modern improvement over bcrypt and the current best practice for secure password storage. The password hash is securely stored in a system environment variable and used for verifying user-submitted passwords.
