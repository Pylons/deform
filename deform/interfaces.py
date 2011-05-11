class FileUploadTempStore(object):
    """
    The :class:`deform.FileUploadWidget` requires as its first
    argument a ``tmpstore``.  Such a tmpstore will implement this
    interface: an object implementing the FileUploadTempStore
    interface should implement the methods attached to this
    description.

    Effectively, this interface is a subset of the ``dict`` interface
    plus an additional method named ``preview_url``.  In fact, the
    simplest possible implementation of this interface is:

    .. code-block:: python

       class MemoryTmpStore(dict):
           def preview_url(self, name):
               return None

    However, the :class:`deform.FileUploadWidget` does not remove data
    from the tempstore implementation it uses (it doesn't have enough
    information to be able to do so), and it is job of the tempstore
    implementation itself to expire items which haven't been accessed
    in a while.

    Therefore, the above ``MemoryTmpStore`` implementation is
    generally unsuitable for production, as the data put into it is
    not automatically evicted over time and file upload data provided
    by untrusted users is usually unsuitable for storage in RAM.  It's
    more likely that an implementation in your application will center
    around a sessioning library (such as Beaker) that does data
    eviction and which stores file upload data in persistent storage.
    """

    def __setitem__(self, name, value):
        """
        Set a value.
        """

    def __getitem__(self, name):
        """
        Get a value.
        """

    def get(self, name, default=None):
        """
        Same as dict.get.
        """

    def __contains__(self, name):
        """
        This should return `True` if we have a value for the
        name supplied, `False` otherwise.
        """
        
    def preview_url(self, name):
        """
        Return the preview URL for the item previously placed into the
        tmpstore named ``name`` or ``None`` if there is no preview for
        ``name`` available (or if this tmpstore does not support
        previewable items).  This item should typically return a URL
        to a thumbnail image.
        """
        

    
