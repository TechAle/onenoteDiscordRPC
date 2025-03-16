import threading
import time

from pypresence import Presence, DiscordNotFound


class DiscordRPC:
    discord = None
    def __init__(self, client_id: str, main_thread):
        self.client_id = client_id
        self.main_thread = main_thread
        self.rpc = None

    def start_rpc(self):
        """Avvia la connessione RPC con Discord."""
        try:
            self.rpc = Presence(self.client_id)
            self.rpc.connect()
            threading.Thread(target=self.checkMainThread).start()
            print("Connessione RPC avviata con successo!")
        except DiscordNotFound:
            print("Errore: Discord non è in esecuzione.")
            raise

    def checkMainThread(self):
        while True:
            if not self.main_thread.is_alive():
                self.close_rpc()
                break

    def close_rpc(self):
        """Chiude la connessione RPC."""
        if self.rpc:
            self.rpc.close()
            print("Connessione RPC chiusa.")

    def modify_presence(self, **kwargs):
        """
        Modifica la Rich Presence di Discord.
        :param kwargs: Parametri per la presenza (es. state, details, large_image, ecc.)
        """
        if self.rpc:
            try:
                self.rpc.update(**kwargs)
                print("Presenza modificata con successo!")
            except Exception as e:
                print(f"Errore durante la modifica della presenza: {e}")
        else:
            print("Errore: RPC non avviato. Chiama start_rpc() prima.")




def openDiscord():
    DiscordRPC.discord = DiscordRPC("1084765396344782868", threading.current_thread())
    DiscordRPC.discord.start_rpc()
    DiscordRPC.discord.modify_presence(
        state="...",
        details="Caricamento...",
        large_image="pic",
        large_text="Made with tears",
        start=time.time(),  # Timestamp di inizio
        buttons=[{"label": "Github", "url": "https://github.com/TechAle/onenoteDiscordRPC"}]
    )


def closeDiscord():
    if type(DiscordRPC.discord) == DiscordRPC:
        # noinspection PyUnresolvedReferences
        DiscordRPC.discord.close_rpc()