def byline(fh, chunksize=4096):
    """
    Implement by line buffering for stream types which have read but no
    readline.
    """
    eof = False
    tail = ""
    while not eof:
        # Grab enough chunks to get a newline
        chunks = [tail]
        while True:
            chunk = fh.read(chunksize)
            chunks.append(chunk)
            if '\n' in chunk:
                break

        # Join the chunks and split on new lines, yielding one line at a time
        lines = "".join(chunks).splitlines()
        for line in lines[:-1]:
            yield line
            
        # The final line may be incomplete.  Set it as the first chunk of the
        # next set of reads
        tail = lines[-1]

    # At the end of file.  Emit the last line by itself
    if tail: yield tail


