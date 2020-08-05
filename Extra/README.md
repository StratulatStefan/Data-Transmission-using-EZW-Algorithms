### In acest director se gasesc scripturi pentru invatare. 
### Atunci cand, in proiectul mare, am nevoie de o anumita functionalitate extra (o optimizare), pe care nu o stapanesc foarte bine, trebuie sa incerc, mai intai, sa o implementez separat.
  * Paralelizarea executiei unei functii peste mai multe date de intrare. 
    * Necesara in cadrul operatiei de convolutie a imaginii cu un kernel;
    * Aceasta operatie este foarte costisitoare si, in functie de dimensiunea kernelului, poate genera timpi foarte mari de executie.
    * Avand in vedere ca in cadrul convolutie operatiile sunt independente, aceasta operatie poate fi usor paralelizata. 
    * Avem nevoie sa partitionam imaginea in mai multe subimagini, sa efectuam convolutia peste fiecare subimagine, si sa compunem imaginea finala pe baza rezultatelor generate de procese.
