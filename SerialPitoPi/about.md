### Incercam sa ilustram posibilitatea comunicarii prin UART (seriale) dintre cele doua Raspberry PI.
  * Conectam cele 2 RPi, astfel incat sa aiba Ground comun, si RX <-> TX.
  * script-uri
    * transmitter.py este un script rulat pe Raspberry Pi 4B
      * acesta este script-ul din care se vor trimite mesaje catre receiver
    * receiver.py este un script rulat pe Raspberry Pi 3B+
      * acesta este script-ul care va citi si afisa mesajele primite de la transmitter
