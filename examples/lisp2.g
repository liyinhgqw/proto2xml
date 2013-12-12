parser Lisp:
    ignore:      r'\s+'
    token NUM:   r'[0-9]+'
    token STR:   r'([^\\"]+|\\.)*'

    rule expr:   STR             {{ return ('str',STR) }}
               | NUM             {{ return ('num',atoi(NUM)) }}
               | r"\("           
                        {{ e = [] }}             # initialize the list
                 ( expr {{ e.append(expr) }} ) * # put each expr into the list
                 r"\)"  {{ return e }}           # return the list
