import asyncio
import random
import sys




class SERVER:
   def __init__(self, host="0.0.0.0", port=5000):
       self.host = host
       self.port = port
       self.subscribers = []  # Lista dei client connessi
       self.led = True
       self.temp = random.randint(17, 34)
       self.umidita = random.randint(10, 70)


   def sottoscrivi(self, writer):
       if writer not in self.subscribers:
           self.subscribers.append(writer)


   def rimuovi(self, writer):
       if writer in self.subscribers:
           self.subscribers.remove(writer)


   async def esegui_comando(self, comando, writer, indirizzo):
       comando_upper = comando.upper()
       risposta = ""


       if comando_upper.startswith("TEMP"):
           risposta = f"TEMPERATURA: {self.temp}°C"
           print(f"[RISPOSTA] {indirizzo} -> {risposta}")


       elif comando_upper.startswith("UMIDITA"):
           risposta = f"UMIDITÀ: {self.umidita}%"
           print(f"[RISPOSTA] {indirizzo} -> {risposta}")


       elif comando_upper.startswith("LED ON"):
           self.led = True
           risposta = "LED ACCESO"
           print(f"[LED] {indirizzo} ha acceso il LED")


       elif comando_upper.startswith("LED OFF"):
           self.led = False
           risposta = "LED SPENTO"
           print(f"[LED] {indirizzo} ha spento il LED")


       elif comando_upper.startswith("STATO"):
           risposta = f"STATO: TEMP={self.temp}, UMIDITA={self.umidita}, LED={'ON' if self.led else 'OFF'}"
           print(f"[RISPOSTA] {indirizzo} -> {risposta}")


       elif comando_upper.startswith("QUIT"):
           risposta = "Arrivederci!"
           writer.write(f"{risposta}\n".encode())
           await writer.drain()
           writer.close()
           return


       else:
           risposta = "Comando sconosciuto"


       # Invia la risposta al client che ha fatto la richiesta
       try:
           writer.write(f"{risposta}\n".encode())
           await writer.drain()
       except ConnectionError:
           print(f"[ERRORE] Impossibile rispondere a {indirizzo}")


   async def gestisci_client(self, reader, writer):
       indirizzo = writer.get_extra_info("peername")
       print(f"[CONNESSIONE] {indirizzo}")
       self.sottoscrivi(writer)


       try:
           while True:
               dati = await reader.readline()
               if not dati:
                   break


               comando = dati.decode().strip()
               if not comando:
                   continue


               print(f"[RICEVUTO] '{comando}' da {indirizzo}")
               await self.esegui_comando(comando, writer, indirizzo)


       except ConnectionError:
           pass
       finally:
           self.rimuovi(writer)
           print(f"[DISCONNESSIONE] {indirizzo}")
           writer.close()
           try:
               await writer.wait_closed()
           except ConnectionError:
               pass


   async def avvia(self):
       server = await asyncio.start_server(self.gestisci_client, self.host, self.port)
       print(f"[SERVER] In ascolto su {self.host}:{self.port}")
       async with server:
           await server.serve_forever()




if __name__ == "__main__":
   s = SERVER()
   try:
       asyncio.run(s.avvia())
   except KeyboardInterrupt:
       print("\n[STOP] Server interrotto")
