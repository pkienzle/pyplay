import java.io.File;
import java.io.IOException;
import java.io.RandomAccessFile;
import java.io.FileOutputStream;

public class lock {

	/**
	 * @param args
	 * @throws IOException 
	 */
	public static void main(String[] args) throws IOException {

		File filename = new File("journal");
		// rws forces flush after each write
		//RandomAccessFile handle = new RandomAccessFile(filename, "rws");
		FileOutputStream handle = new FileOutputStream(filename, true);
		System.out.print("opened > ");
		System.in.read();
                System.out.println("locking...");
		handle.getChannel().lock(); // maybe doesn't release
		// handle.seek(handle.length()); // no seek relative to end of file
		handle.write("java write\n".getBytes());
		System.out.print("locked > ");
		System.in.read();
		handle.close();
		// lock.release();
		System.out.print("closed > ");
		System.in.read();
	}

}
