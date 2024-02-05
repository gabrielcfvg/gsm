
# ---------------------------------------------------------------------------- #
#                                    imports                                   #
# ---------------------------------------------------------------------------- #

# ------------------------------- test targets ------------------------------- #
from gsm.project_files._files_utils import hash_file, is_valid_hash, HEX_DIGITS

# ---------------------------------- builtin --------------------------------- #
from pathlib import Path
from os import urandom



def write_file(path: Path, content: str | bytes):

    assert path.parent.is_dir()
    assert not path.exists()

    content_bytes = bytes(content, "utf-8") if isinstance(content, str) else content
    with open(path, 'xb') as file:
        file.write(content_bytes)

def test_hash_file(tmp_path: Path):

    # test with empty file
    empty_file = tmp_path / "empty_file"
    write_file(empty_file, "")
    assert is_valid_hash(hash_file(empty_file))

    # test with non-empty file
    non_empty_file = tmp_path / "file"
    non_empty_content = "this is a test"
    write_file(non_empty_file, non_empty_content)
    assert is_valid_hash(hash_file(non_empty_file))

    # test with binary/non-text file
    binary_file = tmp_path / "binary_file"
    binary_file_content = urandom(10)
    write_file(binary_file, binary_file_content)
    assert is_valid_hash(hash_file(binary_file))


def test_is_valid_hash(tmp_path: Path):

    # hash from any file must be valid
    test_file = tmp_path / "test_file"
    write_file(test_file, "this is a test")
    result_hash = hash_file(test_file)
    assert is_valid_hash(result_hash)

    # from the resulte we can see which is the hex digest size
    # the size must be always the same
    HEX_DIGEST_SIZE = len(result_hash)


    # valid hash
    for ch in HEX_DIGITS:
        assert is_valid_hash(ch * HEX_DIGEST_SIZE)

    for ch in [chr(ch_idx) for ch_idx in range(0, 0x10FFFF)]: # all unicode characters
        
        if ch in HEX_DIGITS:
            continue

        assert not is_valid_hash(ch + (HEX_DIGITS[0] * (HEX_DIGEST_SIZE - 1)))
