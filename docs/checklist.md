CHECKLIST:

1. Opisane `Story` od strony usera:
    * co chcę zobaczyć.
    * gdzie to ma być.
    * Jak użytkownik będzie to obsługiwał.
    * Schemat "As a user I would like..."
      > As a user, I would like to see a list of transactions

2. `Task` powinien opisywać co ma robić dana funkcja:
    * Jasna nazwa funkcji, input, output np.
    * Ogólny opis jak chcemy osiągnąć nasz cel.

    ```   
   get_total_outflow(zmienna: int) -> dict:
       dict = {"kwota": zmienna} 
       return dict
   ```
    * dokładnie jak ma być wyliczanie pole (nie sposób, ale koncepcyjnie).
   
3. Przypisana osoba do `taska`

2. Jeżeli jesteśmy zależni od innego taska to opisane kiedy mamy go robić:
    * po zmergowaniu SN-nr_XYZ

4. Checklista (acceptance criteria) w tasku:
   1. Obsługa wyjątków (walidacja inputu)   
   1. Test manualny zaliczony
      * Da się zrobić bez błędów to, co było opisane w `Story`
   1. Kod przetestowany flake8 i isort
   1. Zrobione code review
      * Osoba, która robi review też sprawdza czy działa
   1. Branch zmergowany do developa
   