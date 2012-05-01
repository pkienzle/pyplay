I coded this wrapper around ftplib to do the common case of fetching a single file and exiting.

The advantage over urllib is that it doesn't need to hold the file in memory, and it can continue
downloading after a lost connection.

