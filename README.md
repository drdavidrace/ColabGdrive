# ColabGDrive
This is a python repository for basic tools for working with Google Drive in a Colaboratory environment for BigData exploration.  It is primarily targeted at using 
a reasonable set of assumptions on the Folder design to access files and directories in a Google Drive from Colaboratory.  (It may also work with Jupyter, but that
will be reserved for later.)  The Basice assumptions are:

*  The structure of the folders will be very "Linux" like
*  There will not be a bunch of multiple parent files/folders
*  There will not (should not) be multiple files/folders in a folder with the same name

The basis for these assumptions are:
*  The general "directory/file" assumption maps well to our assumption of the way data is stored
*  Multi-parent configurations makes it difficult to move down a folder-tree
  *  There is an exponential growth in tree constructs if multi-parent configurations are allowed
*  The same name is "weird".  We are accustomed to deal with versions, but the same name is challenging.

These assumptions for the basis for our working code.These

WARNING:  Initially the code us function oriented, but it may change to object oriented in the future.  The Linux/Unix command line capabilities are function oriented; however,
the Google Drive API is object oriented so a decision has to be made for diving the original design.
