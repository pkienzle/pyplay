#include <stdlib.h>
#include <unistd.h>
#include <stdio.h>
#include <fcntl.h>
#include <string.h>

int main(int argc, char *argv[])
{
  int i;
  int fd = open("journal", O_WRONLY|O_CREAT|O_APPEND);

  struct flock lock;
  lock.l_type = F_WRLCK;
  lock.l_whence = SEEK_SET;
  lock.l_start = 0;
  lock.l_len = 0;
  lock.l_pid = 0;

  printf("opened > ");
  getchar();

  printf("locking...\n");
  if (fcntl(fd, F_SETLKW, &lock) == -1) { 
    printf("could not obtain lock\n");
    exit(1);
  }

  if (argc > 1) {
    for (i=1; i<argc; i++) {
      write(fd, argv[i], strlen(argv[i]));
      if (i < argc-1) write(fd, " ", 1);
    }
    write(fd, "\n", 1);
  } else {
    write(fd, "c output\n", 9);
  }
  fsync(fd);
  printf("locked > ");
  getchar();

  lock.l_type = F_UNLCK;
  if (fcntl(fd, F_SETLKW, &lock) == -1) {
    printf("could not release lock\n");
    exit(1);
  }
  close(fd);

  printf("unlocked > ");
  getchar();

  exit(0);
}
