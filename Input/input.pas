VAR A;
VAR B;

VAR Q;
VAR K;
VAR R;

PROCEDURE PRINTA;
  BEGIN
    FOR A := 1 TO 5 DO
        WRITE(Q);
  END;

PROCEDURE PRINTB;
  BEGIN
    FOR B := 1 TO 5 DO
        WRITE(K);
  END;

BEGIN
	Q := 666;
	K := 999;

	COBEGIN
   	CALL PRINTA;
   	CALL PRINTB;
  COEND;

  R := 4;
  WRITE(R);

END.