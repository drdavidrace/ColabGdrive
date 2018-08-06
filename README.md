# ColabGDrive
This is a python repository for basic tools for working with Google Drive in a Colaboratory environment for BigData.  It is designed to be imported into a *Colaboratory* program so that data can be efficiently moved between the Colaboratory instantiation's local drive and the users Google Drive.  It is primarily targeted at a usecase of a reasonable set of assumptions on the Google Drive Folder design to access files and directories in a Google Drive.  (It may also work with Jupyter, but that
will be reserved for later.)  The Basice assumptions are:

*  The structure of the folders will be very "Linux" like
>*  Some of the basic "Linux" commands are available; however, they are designed for moving between the local environment and the Google Drive.
>*  The commands are very basic at this point.  Maybe they will be expanded in the future.
*  There will not be multiple parent files/folders
>*  It is easy to have multiple files/folders for an individual file; however, that will be a problem for the semantics.
*  There should not be multiple files/folders in a folder with the same name
>*  Google Drive allows the same names since it actually uses a separate tag for tracking files.  This isn't just versioning, but rather a feature that exists in a Google Drive.
>*  This is very problematic for many semantic capabilities.

The basis for these assumptions are:
*  The general "directory/file" assumption maps well to our assumption of the way data is stored
*  Multi-parent configurations makes it difficult to move down a folder-tree
  *  There is an exponential growth in tree constructs if multi-parent configurations are allowed
*  The same name is "weird".  We are accustomed to deal with versions, but the same name is challenging.

As I get more experience with Google's methodology, these assumption may be modified.

##Testing

The testing is primarily performed within Colaboratory, so it is a little laborous in this initial testing.

WARNING:  This code creates an *"object"* for the Google Drive, then the functionality is performed by methods of the object.  
