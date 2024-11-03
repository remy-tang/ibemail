from dataclasses import dataclass, field, MISSING

# === Base configs === #


@dataclass
class ServerConfig:  # SMTP Server
    hostname: str = MISSING
    port: int = MISSING


@dataclass
class LocalhostConfig(ServerConfig):
    hostname: str = "localhost"
    port: int = 8025


@dataclass
class SMTP2GOConfig(ServerConfig):
    hostname: str = "mail.smtp2go.com"
    port: int = 587


@dataclass
class ClientConfig:
    sk: str = MISSING
    cert: str = MISSING
    address: str = MISSING


@dataclass
class CAConfig(ClientConfig):  # Certificate Authority
    sk: str = "./keys/sk_ca.pem"
    cert: str = " ./certificates/cert_ca.pem"
    address: str = "ca@pesto.cyber"


@dataclass
class AliceConfig(ClientConfig):  # Sender information
    sk: str = "./keys/sk_alice.pem"
    cert: str = "./certificates/cert_alice.pem"
    address: str = "alice@pesto.cyber"


@dataclass
class BobConfig(ClientConfig):  # Recipient information
    sk: str = "./keys/sk_bob.pem"
    cert: str = "./certificates/cert_bob.pem"
    address: str = "bob@pesto.cyber"


# === Full configs === #


@dataclass
class Scenario:
    smtp_server: ServerConfig = MISSING
    ca: ClientConfig = MISSING
    sender: ClientConfig = MISSING
    recipient: ClientConfig = MISSING


@dataclass
class LocalhostScenario(Scenario):
    smtp_server: ServerConfig = field(default_factory=LocalhostConfig)
    ca: ClientConfig = field(default_factory=CAConfig)
    sender: ClientConfig = field(default_factory=AliceConfig)
    recipient: ClientConfig = field(default_factory=BobConfig)
