# scripts/generate_cert.py
"""Módulo para generar certificados SSL auto-firmados localmente.
Permite habilitar HTTPS seguro en el servidor local de Mónica para que
los navegadores móviles (como Safari en iPhone) permitan usar el micrófono.
"""
import sys
from pathlib import Path

def generate_self_signed():
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        import datetime
    except ImportError:
        print("Instalando dependencia 'cryptography' necesaria para generar certificados SSL...")
        import subprocess
        try:
            # Intentar usar el pip del entorno virtual
            venv_pip = Path(__file__).resolve().parent.parent / "venv" / "Scripts" / "pip.exe"
            if venv_pip.exists():
                subprocess.check_call([str(venv_pip), "install", "cryptography"])
            else:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "cryptography"])
        except Exception as err:
            print(f"Error instalando automáticamente con pip: {err}")
            print("Por favor, instala la librería manualmente ejecutando: venv\\Scripts\\pip.exe install cryptography")
            return
            
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        import datetime

    print("Generando llave privada RSA de 2048 bits...")
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    
    # Obtener IP local de forma dinámica
    import socket
    def get_local_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "192.168.1.9"
            
    local_ip = get_local_ip()
    print(f"IP local detectada: {local_ip}")
    
    # Generar certificado auto-firmado
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "California"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Mónica IA"),
        x509.NameAttribute(NameOID.COMMON_NAME, "Monica Local Server"),
    ])
    
    import ipaddress
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.utcnow())
        .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=3650))
        .add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.DNSName("127.0.0.1"),
                x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
                x509.IPAddress(ipaddress.IPv4Address(local_ip)),
            ]),
            critical=False,
        )
        .sign(key, hashes.SHA256())
    )
    
    # Directorio base
    base_dir = Path(__file__).resolve().parent.parent
    key_path = base_dir / "key.pem"
    cert_path = base_dir / "cert.pem"
    
    # Guardar llave
    with open(key_path, "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ))
        
    # Guardar certificado
    with open(cert_path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
        
    print("\n[OK] Certificados SSL auto-firmados creados con exito!")
    print(f"- Llave Privada: {key_path}")
    print(f"- Certificado: {cert_path}")
    print("\nLa proxima vez que inicies el servidor de Monica, se levantara automaticamente en:")
    print(f"- HTTPS: https://localhost:8000 (desde tu PC)")
    print(f"- HTTPS: https://{local_ip}:8000 (desde tu iPhone)")
    print("\nNota: La primera vez que accedas en tu movil, Safari te mostrara una advertencia de privacidad.")
    print("Simplemente haz clic en 'Mostrar Detalles' -> 'Visitar este sitio' para aceptar tu certificado local.")
    print("¡Una vez hecho, el microfono funcionara a la perfeccion en tu iPhone!")

if __name__ == "__main__":
    generate_self_signed()
