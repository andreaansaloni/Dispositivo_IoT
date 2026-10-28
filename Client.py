import asyncio
import sys


async def main():
   # Connessione al server TCP
   try:
       reader, writer = await asyncio.open_connection("0.0.0.0", 5000)
       print("Connesso al server.")
   except ConnectionRefusedError:
       print("Impossibile connettersi. Assicurati che il server sia attivo.")
       return


   print("\nComandi disponibili:")
   print("- TEMP          (Richiedi temperatura)")
   print("- UMIDITA       (Richiedi umidità)")
   print("- LED ON/OFF    (Accendi o spegni il led)")
   print("- STATO         (Stato del dispositivo)")
   print("- QUIT          (Chiudi connessione)\n")


   while True:
       comando = await asyncio.get_event_loop().run_in_executor(
           None, input, "Inserisci comando: "
       )
       comando = comando.strip()

       if not comando:
           continue


       writer.write(f"{comando}\n".encode())
       await writer.drain()


       if comando.upper() == "QUIT":
           print("Chiusura connessione...")
           break


       # Riceve la risposta dal server
       risposta = await reader.readline()
       if not risposta:
           print("Il server ha chiuso la connessione.")
           break


       print("Server:", risposta.decode().strip())


   # Chiude la connessione
   writer.close()
   await writer.wait_closed()


asyncio.run(main())

