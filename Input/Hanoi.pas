FUNCTION HANOI(VAL N; VAL SOURCE; VAL DESTINATION; VAL HELP);
BEGIN
    IF (N = 1) THEN WRITELN(SOURCE, DESTINATION)
    ELSE
    BEGIN
        CALL HANOI(N-1, SOURCE, HELP, DESTINATION);
        WRITELN(SOURCE, DESTINATION);
        CALL HANOI(N-1, HELP, DESTINATION, SOURCE)
    END;
END;

BEGIN
    CALL HANOI(4,1,3,2);
END.