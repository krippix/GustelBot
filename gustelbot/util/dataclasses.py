from dataclasses import dataclass


@dataclass
class File:
    """
    Representation of a file entry in the database.
    size
    guild_id
    user_id
    display_name
    file_name
    file_hash
    seconds
    tags
    id
    """
    size: int
    guild_id: int
    user_id: int
    display_name: str
    file_name: str
    file_hash: str
    seconds: int
    tags: tuple = ()
    id: int = None
