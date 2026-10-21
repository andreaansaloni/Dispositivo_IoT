# broker.py
#   sub:topic            -> sottoscrive il client al topic
#   pub:topic:messaggio  -> invia il messaggio a tutti i sottoscritti al topic

import asyncio

class Broker:
    def __init__(self, host="0.0.0.0", port=5000):
        self.host = host
        self.port = port
        self.subscribers = {}   # topic -> lista dei writer dei client sottoscritti

    def sottoscrivi(self, topic, writer):
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        if writer not in self.subscribers[topic]:   # evita doppioni
            self.subscribers[topic].append(writer)

    def rimuovi(self, writer):
        for lista in self.subscribers.values():
            if writer in lista:
                lista.remove(writer)

    async def pubblica(self, topic, messaggio):
        if topic not in self.subscribers:
            print(f"[NESSUN SUBSCRIBER] Nessuno sottoscritto a '{topic}'")
            return

        print(f"[PUBBLICAZIONE] '{topic}': {messaggio}")
        # si scorre una copia: durante drain() un altro client può disconnettersi
        for writer in list(self.subscribers[topic]):
            try:
                writer.write(f"[{topic}] {messaggio}\n".encode())
                await writer.drain()
            except ConnectionError:
                print("[ERRORE] Invio fallito a un subscriber")


    async def esegui_comando(self, comando, writer, indirizzo):
        if comando.startswith("sub:"):
            topic = comando[4:]
            self.sottoscrivi(topic, writer)
            print(f"[SOTTOSCRIZIONE] {indirizzo} -> '{topic}'")

        elif comando.startswith("pub:"):
            parti = comando.split(":", 2)
            if len(parti) == 3:
                _, topic, messaggio = parti
                await self.pubblica(topic, messaggio)
            else:
                print(f"[ERRORE] Pubblicazione malformata: {comando}")

        else:
            print(f"[ERRORE] Comando sconosciuto: {comando}")

    async def gestisci_client(self, reader, writer):
        indirizzo = writer.get_extra_info("peername")
        print(f"[CONNESSIONE] {indirizzo}")

        try:
            while True:
                dati = await reader.readline()
                if not dati:
                    break
                comando = dati.decode().strip()
                print(f"[RICEVUTO] {comando} da {indirizzo}")
                await self.esegui_comando(comando, writer, indirizzo)
        except ConnectionError:
            pass
        finally:
            self.rimuovi(writer)
            print(f"[DISCONNESSIONE] {indirizzo}")
            writer.close()
            await writer.wait_closed()

    async def avvia(self):
        server = await asyncio.start_server(self.gestisci_client, self.host, self.port)
        print(f"[BROKER] In ascolto su {self.host}:{self.port}")
        async with server:
            await server.serve_forever()


if __name__ == "__main__":
    broker = Broker()
    try:
        asyncio.run(broker.avvia())
    except KeyboardInterrupt:
        print("[STOP] Broker interrotto")