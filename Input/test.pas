CONST
        A=10;
VAR
        B1,C,F;

    PROCEDURE ONE;
    CONST
            A=5;
    VAR
            C1,D1;
    BEGIN
            F := 50;
            C1 := 1;
            D1 := 1;
            IF C1+1 = 2 THEN
                WRITELN(F)
            ELSE
                F := 2;
                WRITE(F);
    END;
BEGIN
            B1:=11+A*(A-A);
            CALL ONE;
END.