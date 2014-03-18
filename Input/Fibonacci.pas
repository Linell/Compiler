VAR A;

FUNCTION FIB(VAL X);
    BEGIN
        IF (X = 1) THEN FIB := 0
        ELSE
        IF (X = 2) THEN FIB := 1
        ELSE FIB := CALL FIB(X-1) + CALL FIB(X-2)
    END;
    
BEGIN
    FOR A := 1 TO 19 DO
        WRITE(CALL FIB(A));
    WRITELN(CALL FIB(A));
END.