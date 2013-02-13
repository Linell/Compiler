CONST
    A = 5, B = 10;
VAR
    C, D, E;

PROCEDURE ONE;
    VAR B, C;

    PROCEDURE TWO;
        VAR C, D;
        BEGIN
            IF C = D THEN
                CALL TWO;
            CASE C+1 OF
             3:WRITELN(A,B,C);
             B:IF A+1=B THEN
                IF 10=A THEN ELSE WRITE(A,C)
               ELSE WRITE(B,C);
            CEND;
        END;

    PROCEDURE THREE;
        VAR X, Y, Z, A, B, C;
        BEGIN
            IF C < X THEN
            BEGIN
                CALL THREE;
                CALL TWO;
                WRITELN(ONE);
            END;
        END;

    BEGIN
        IF B <= -(5 + C * A) THEN
            FOR B1:=10 DOWNTO A DO
                CALL ONE;
    END;

BEGIN
    C := +(C + 1);
    CALL ONE;
    WHILE A > A / A DO
        WHILE B >= B DO
            IF ODD E THEN
                E := E - 1;
END.
