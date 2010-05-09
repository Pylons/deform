class FileUploadTempStore(object):
    """
    The :class:`deform.FileUploadWidget` requires as its first
    argument a ``tmpstore``.  This should be an instance of an object
    that implements this interface.

    A an object implementing the FileUploadTempStore interface should
    implement these methods.  Effectively, the interface is a subset
    of the ``dict`` interface plus an additional method named
    ``preview_url``.
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

    def preview_url(self, name):
        """
        Return the preview URL for the item previously placed into the
        tmpstore named ``name`` or ``None`` if there is no preview for
        ``name`` available (or if this tmpstore does not support
        previewable items).
        """
        

    
