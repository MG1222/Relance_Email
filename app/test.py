import smtplib
import ssl

def check_smtp_server(smtp_server, port):
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP(smtp_server, port) as server:
            if port == "587":
                server.starttls(context=context)
            server.noop()  # une commande simple pour vérifier la connexion
        print(f"Connexion réussie à {smtp_server} sur le port {port}")
    except Exception as e:
        print(f"Échec de la connexion à {smtp_server} sur le port {port}: {e}")

# Remplacez par votre serveur SMTP et port
smtp_server = "mail.akema.fr"
smtp_port = 587


if __name__ == "__main__":
    check_smtp_server(smtp_server, smtp_port)