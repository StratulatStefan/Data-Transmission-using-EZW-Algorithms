### Incercam sa ilustram posibilitatea comunicarii prin UART (seriale) dintre cele doua Raspberry PI.
  * Idei
    * Format pache
      * bit Start : mereu LOW
      * pachet date : datele efective 1 octet
      * bit Stop : mereu HIGH
    * Raspberry PI are 2 interfete UART
      * PL011 UART
          * pentru unele RPi, este folosit pentru modulul de Bluetooth, iar pentru altele, este folosit pentru consola de output
          * Se identifica prin portul ttyAMA0 (serial 1)
      * mini UART
          * pentru unele RPi, este folosit pentru consola de output (cazul nostru)
          * [asadar, vom folosi aceasta interfata pentru a trimite si citi date]
          * lucreaza la frecventa procesorului; asadar, frecventa UART si baud-rate vor varia direct proportional cu frecventa procesor; din acest motiv, poate fi instabil si poate genera pierderea sau coruperea datelor
          * By default, este mapat pe pinii UART (RX si TX)
          * Se identifica prin portul ttyS0 (serial 0)
    * Pentru a verifica pe ce pin are loc transmisia seriala (PL011 sau mini), vizualizam dispozitivele din /dev si verificam maparea cu serial 0.
    * Avand in vedere faptul ca PL011 este mai performant, in cazul in care by default este setat mini UART si vrem sa setam PL011, efectuam urm.
        * sudo nano /boot/config.txt -> dtoverlay = pi3-miniuart-bt sau dtoverlay = pi3-disable-bt [la final]
  * Activam UART pe RPi.
     * sudo raspi-config
         * Interfacing Options -> Serial -> No to making login shell accesible over serial -> Yes to enable serial hardware port
  * Conectam cele 2 RPi, astfel incat sa aiba Ground comun, si RX <-> TX.
  * script-uri
    * transmitter.py este un script rulat pe Raspberry Pi 4B
      * acesta este script-ul din care se vor trimite mesaje catre receiver
    * receiver.py este un script rulat pe Raspberry Pi 3B+
      * acesta este script-ul care va citi si afisa mesajele primite de la transmitter

### References
  * https://www.electronicwings.com/raspberry-pi/raspberry-pi-uart-communication-using-python-and-c
  * https://raspberrypi.stackexchange.com/questions/29027/how-should-i-properly-communicate-2-raspberry-pi-via-uart
