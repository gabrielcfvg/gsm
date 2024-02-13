# -------------------------------- third party ------------------------------- #
import msgspec



class GsmFileStruct(msgspec.Struct, forbid_unknown_fields=True):
    """
    This class provides a single source of truth for all the msgspec structs used in the project.
    The configurations that shall be used by all structs should be set here.
    """
