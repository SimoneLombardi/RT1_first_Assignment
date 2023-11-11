# RT1_first_Assignment

## Assignment 1, Lombardi Simone

___

### Flow chart del programma
![Blank diagram](https://github.com/SimoneLombardi/RT1_first_Assignment/assets/146358714/e693282b-d512-477f-900a-826318db664e)

___

### Desctizioni delle funzioni utilizzate:

***set_ancor_token()*** <br>
Questa funzione esegue la prima parte dell'inizializzazione del programma, chiamando la funzione ***create_token_list*** guarda tutta l'arena
e inserisce in una lista tutte i codici dei token presenti. Dopodichè procede tramite un intero casuale a scegliere uno dei token come "ancora"
dove raggruppare tutti gli graltri token. E restituisce al programma in delle variabili la lista dei codici ed il codice dell'ancora.

***create_grabbed_token_list(token_code(int), token_list(list), grabbed_token_list(list))*** <br>
Dopo aver creato la lista con tutti i codici dei token ne creo una dove memorizzare i codici dei token già spostati, la creazione di tale lista
parte dal controllare se l'argomento *grabbed_token_list* è vuoto o no dato che utilizzo la stessa funzione sia per CREARE la lista che per AGGIORNARLA.
Se la lista è vuota inserisco tanti elementi temporanei quanti sono gli elementi della lista *token_list*. Nella prima chiamata di questa funzione 
l'argomento *token_code* conterrà il codice del token ancora generato nella funzione ***set_ancor_token()***.

Finita la parte di inizializzazione inizio un ciclo while con una variabile *CONTROL* inizializzata a zero("False"), finchè le due liste
*grabbed_token_list* e *token_list* sono diverse tale variabile resterà zero.

***find_movable_token(grabbed_token_list(list))*** <br>
La prima funzione svolta all'interno del ciclo while cerca nell'area di lavoro un token che abbia un codice non presente in *grabbed_token_list*, continuando
a fare delle rotazioni fino a che la sua condizione non è vera per almeno 1 dei token visibili. Nel momento che questa funzione termina inoltre il robot 
punta già nella direzione del token da spostare.

***go_to_token(token_code(int), ancorDistTol(float))*** <br>
Questa è la funzione di movimento dove il robot corregge il suo orientamento ed la sua posizione in modo da poter eseguire la funzione ***R.grab()*** sul 
token passato come argomento. 
Le funzioni aggiuntive chiamate all'interno di questa funzione sono:

1. *get_token_info(token_code(int))*<br>
    - tramite la funzione *R.see()* restituisce le variabili di posizione (token_code.dist) e angolo (token_code.rot_y)
2. *turn_parameter(ang(float))*<br>
    - tramite una formula ottenuta da prove sperimentali restituisce un valore di velocità angolare per completare una rotazione di *ang* gradi
3. *drive_parameter(dist(float))*<br>
    - tramite una formula ottenuta da prove sperimentali restituisce un valore di velocità lineare per completare uno spostamento di *dist* metri
4. *get_ancor_tol(token_code(int))*<br>
    - fornisce il numero di token che entro certi valori di distanza e angolazione vengono considerati come "davanti" al token *token_code

Questa funzione di avvicinamento funziona in tre fasi:

1. Correzione dell'angolazione, tramite una tolleranza (visto che difficilmente l'angolo risulterà pari a zero)
2. Correzione della distanza, valutando se devo eseguire *R.grab()* oppure *R.release()*
3. Esecuzione di *R.grab()* o *R.release()*

Nel primo caso la correzione dell'angolo avviene con il seguente procedimento:
Si recuperano le informazioni del token con *get_token_info(token_code(int))*, tramite la funzione *turn_parameter(ang(float))* ottengo una velocità angolare
ed un tempo di rotazione, infine tramite *turn(speed, time)* eseguo la rotazione finchè ang < tolleranza+correzione.
La correzione della tolleranza è necessaria nel caso li robot si trovasse bloccato tra due valori opposti di orientamento, ang e -ang. Dovesse succedere è possibile che 
la velocità trovata ed il tempo trovati da *turn_parameter(ang(float))* non permettano di scendere sotto la tolleranza entrando in un loop infinito.
La variabile correzione incrementa di 0.1 gradi la tolleranza ogni ciclo per essere sicuro che eventualmente il robot possa procedere con l'esecuzione.

Nel secondo caso invece seppur con la stessa logica non è necessaria la correzione della tolleranza dato che la velocità minima che posso ottenere da *drive_parameter(dist(float))*
è 1, quindi anche nel caso peggiore il robot scenderà sicuramente sotto la tolleranza di distanza per eseguire *R.grab()*

Infine nel terzo caso devo valutare se eseguire *R.grab()* oppure *R.release()* per evitare di incorrere nell'errore AlreadyHoldingSomething e causare la prematura chiusura del programma.
Utilizzando l'argomento *ancorDistTol* che serve per modificare la tolleranza nel caso due a seconda che il robot si stia avvicinando ad un token qualsiasi o al token ancora, 
se *ancorDistTol* è NULLO allora eseguo *R.grab()* altrimento se è NON NULLO *R.release()*.

***create_grabbed_token_list(token_code(int), token_list(list), grabbed_token_list(list))*** <br>
Stessa funzione spiegata precedentemente, ma utilizzata per aggiornare la lista anzichè crearla.

***list_comparison(token_list(list), grabbed_token_list(list)*** <br>
Questa funzione restituisce 1 se le due liste passate sono uguali, 0 in caso contrario.
Posso fare con un singolo ciclo dato che per costruzione delle due liste se un elemento è presente in entrambe avrà il medesimo indice.

Il ciclo prosegue finchè la variabile *CONOTROL* modificata dall'ultima funzione non cambia da 0 a 1.
