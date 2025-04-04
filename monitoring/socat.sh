sudo apt install socat

socat TCP4-LISTEN:4041,fork TCP4:localhost:4040 &
