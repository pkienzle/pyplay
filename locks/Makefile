all: lock lock.class

lock: lock.c
	gcc -Wall -o $@ $<

lock.class: lock.java
	javac $<
