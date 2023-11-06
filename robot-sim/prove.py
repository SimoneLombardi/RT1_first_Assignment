
import random

def closest_token(tok_list):
    leng = len(tok_list)
    # definisco gli indici in precedenza per poter gestire il ciclo meglio
   

    for i in range(leng): # il primo ciclo passa su tutti gli elementi 
        
        control = 1
        for j in range(0, leng-i-1): # ogni volta che ne trovo uno più piccolo posso ripartire da quello
            print(j, i)
            x = tok_list[j]
            y = tok_list[j+1]
            if x > y:
                control = 0
                break
        
        if control == 1:
                print(i)
                return i 




def main():
    rand_list=[]
    n=10
    for i in range(n):
        rand_list.append(random.randint(1,3))
    print(rand_list)

    lowest = closest_token(rand_list)
    output = sorted(rand_list)
    print(rand_list[lowest])
    print("\n\n\n\n\n")
    print(output)

main()

