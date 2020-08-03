# Discrete Wavelet Transform
#### DWT este primul pas al algoritmului EZW si reprezinta descompunerea imaginii in 4 sub-benzi in domeniul frecventa.
  * Frecventele joase corespund unui bandwidth intre 0 si pi/2
  * Frecventele inalte corespun unui bandwidth intre pi/2 si pi.
#### Cele patru sub-benzi rezulta prin aplicarea unor filtre orizontale si verticale asupra imaginii originale.
<table> 
  <tr>
    <td>LL</td>
    <td>HL</td>
  </tr>
  <tr>
    <td>LH</td>
    <td>HH</td>
  </tr>
</table>

#### LH, HL si HH reprezinta coeficientii ce corespund detaliilor din imagine, iar LL, elementele generale. LL va fi folosit pentru descompunerea la urmatorul nivel, pentru a
obtine si mai multe detalii.

#### Exista o multitudine de tipuri de wavelets, fiecare avand anumite particularitati. In esenta, fiecare tip poate fi definit printr-un filtru (kernel) de dimensiune data, care se aplica asupra liniilor (orizontal) si coloanelor (vertical) in diverse moduri. (mai multe detalii in documentul Shahbahrami_Super_computing_Sep_2012.pdf)
  * Convolutie : aplicarea operatiei de convolutie 1D asupra liniilor si salvarea rezultatului intr-o matrice auxiliara, asupra careia se aplica ulterior operatia de convolutie 1D pe coloane
  * Linear-based : la baza este o convolutie, dar mai eficient dpv al memoriei
    * nu se efectueaza convolutia 1D asupra intregii imagini pe linii, ci pe un numar de linii din imagine egal cu dimensiunea filtrului;
    * rezultatul aplicarii acestui filtru pe cele L linii se salveaza intr-un buffer, asupra caruia se aplica ulterior filtrul pe coloane (vertical)
    * rezultatul final al aplicarii filtrului pe coloanele bufferului se salveaza in imaginea rezultata.
    * se repeta procesul pana se parcurg toate liniile
  * Lifting-scheme : presupune 50 % mai putine calcule decat convolutia
    * contine trei faze
      * split : spargerea imaginii in 2 vectori ce contin doar elementele cu index par si index impar din imagine
      * predict : calcularea valorilor high pass pe baza valorilor de la faza anterioara
      * update  : calcularea valorilor low pass pe baza valorilor de la faza anterioara
    * pentru fazele predict si update se folosesc anumite formule (se pot vedea in comentariile din cod)
    * cele trei faze se aplica, mai intai orizontal (pe linii), si mai apoi vertical (pe coloane)
    
#### Wavelet-urile au fost definite prin anumite filtre (convolution si linear-based). 
  * Haar
  * Daubechies 4
  * (Exemple de alte filtre sau extensii ale celor mentionate : Liu-WaveletTransform-2010.pdf)
  
  * In cadrul algoritmului nostru vom folosi filtre de tip 9-tap symmetric quadrature mirror filters (QMF-piramid), doarecere au o buna localizare a elementelor imaginii, trateaza corect muchiile si produce rezultate bune.
