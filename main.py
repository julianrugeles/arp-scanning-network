from scapy.all import ARP, Ether, srp
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import time

# Configuración de SQLAlchemy
Base = declarative_base()

class NetworkDevice(Base):
    __tablename__ = 'network_devices'

    id = Column(Integer, primary_key=True, autoincrement=True)
    scan_date = Column(DateTime, nullable=False)
    ip_address = Column(String(15), nullable=False)
    mac_address = Column(String(17), nullable=False)

def setup_database():
    """Configura la base de datos y crea las tablas."""
    engine = create_engine("postgresql+psycopg2://admin:admin@localhost:5432/admin")
    Base.metadata.create_all(engine)
    return engine

def scan_network(ip_range):
    """Escanea la red y devuelve los dispositivos encontrados."""
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp
    result = srp(packet, timeout=3, verbose=0)[0]

    devices = []
    for sent, received in result:
        devices.append({
            'scan_date': datetime.now(),
            'ip_address': received.psrc,
            'mac_address': received.hwsrc
        })
    return devices

def save_devices_to_db(devices, session):
    """Guarda los dispositivos escaneados en la base de datos."""
    for device in devices:
        network_device = NetworkDevice(
            scan_date=device['scan_date'],
            ip_address=device['ip_address'],
            mac_address=device['mac_address']
        )
        session.add(network_device)
    session.commit()
    print(f"{len(devices)} dispositivos insertados en la base de datos.")

if __name__ == "__main__":
    ip_range = "192.168.1.0/24"
    
    # Configurar la base de datos
    engine = setup_database()
    Session = sessionmaker(bind=engine)
    session = Session()

    # Escanear la red
    while True:
        time.sleep(30)

        devices = scan_network(ip_range)

        # Guardar en la base de datos
        if devices:
            save_devices_to_db(devices, session)
        else:
            print("No se encontraron dispositivos en la red.")
