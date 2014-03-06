CONST
        A=10;
VAR
        B1,C,F;
FUNCTION TEST;
VAR
    L2,L3;
BEGIN
    L2 := 3;
    L3 := 2;
    L2*L3;
END;
    PROCEDURE ONE;
    CONST
            A=5;
    VAR
            C1,D1;
    BEGIN
            F := 50;
            C1 := 1;
            D1 := 1;
            CASE A+1 OF
             6:WRITELN(12);
             3:WRITELN(12);
            CEND;
    END;
BEGIN
            B1:=11+A*(A-A);
            CALL ONE;
END.