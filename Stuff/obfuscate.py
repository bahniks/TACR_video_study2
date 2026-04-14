from __future__ import annotations

import getpass
import hmac
import os
import secrets
import sys
import tempfile

from hashlib import pbkdf2_hmac, sha256
from pathlib import Path


MAGIC = b"TACROBF1"
SALT_SIZE = 16
NONCE_SIZE = 16
MAC_SIZE = 32
CHUNK_SIZE = 1024 * 1024
PBKDF2_ITERATIONS = 200_000

SCRIPT_DIR = Path(__file__).resolve().parent
DISTRACTIONS_DIR = SCRIPT_DIR / "Distractions"
VIDEO_ZIPS = ["videos1.zip", "videos2.zip"]


def derive_keys(password: str, salt: bytes) -> tuple[bytes, bytes]:
    key_material = pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
        dklen=64,
    )
    return key_material[:32], key_material[32:]


def transform_chunk(data: bytes, key: bytes, nonce: bytes, counter: int) -> tuple[bytes, int]:
    output = bytearray(data)
    offset = 0

    while offset < len(output):
        block = sha256(key + nonce + counter.to_bytes(8, "big")).digest()
        block_size = min(len(block), len(output) - offset)
        for index in range(block_size):
            output[offset + index] ^= block[index]
        offset += block_size
        counter += 1

    return bytes(output), counter


def prompt_password() -> str:
    password = getpass.getpass("Enter password for obfuscation: ")
    if not password:
        raise ValueError("Password cannot be empty.")

    confirmation = getpass.getpass("Confirm password: ")
    if password != confirmation:
        raise ValueError("Passwords do not match.")

    return password


def obfuscate_file(source_zip: Path, output_file: Path, password: str) -> None:
    salt = secrets.token_bytes(SALT_SIZE)
    nonce = secrets.token_bytes(NONCE_SIZE)
    encryption_key, mac_key = derive_keys(password, salt)
    header = MAGIC + salt + nonce
    authenticator = hmac.new(mac_key, digestmod="sha256")
    authenticator.update(header)

    temp_path: Path | None = None
    counter = 0

    try:
        with tempfile.NamedTemporaryFile(delete=False, dir=DISTRACTIONS_DIR, suffix=".tmp") as temp_file:
            temp_path = Path(temp_file.name)
            temp_file.write(header)

            with source_zip.open("rb") as source_file:
                while True:
                    chunk = source_file.read(CHUNK_SIZE)
                    if not chunk:
                        break

                    transformed_chunk, counter = transform_chunk(chunk, encryption_key, nonce, counter)
                    temp_file.write(transformed_chunk)
                    authenticator.update(transformed_chunk)

            temp_file.write(authenticator.digest())

        os.replace(temp_path, output_file)
        source_zip.unlink()
    except Exception:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()
        raise


def obfuscate_archive(password: str) -> None:
    if not DISTRACTIONS_DIR.is_dir():
        raise FileNotFoundError(f"Distractions directory not found: {DISTRACTIONS_DIR}")

    for zip_name in VIDEO_ZIPS:
        source_zip = DISTRACTIONS_DIR / zip_name
        output_file = DISTRACTIONS_DIR / zip_name.replace(".zip", ".obf")

        if not source_zip.is_file():
            raise FileNotFoundError(f"Source archive not found: {source_zip}")
        if output_file.exists():
            raise FileExistsError(f"Obfuscated file already exists: {output_file}")

        obfuscate_file(source_zip, output_file, password)


def main() -> int:
    try:
        password = prompt_password()
        obfuscate_archive(password)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    for zip_name in VIDEO_ZIPS:
        obf_name = zip_name.replace(".zip", ".obf")
        print(f"Created obfuscated archive: {obf_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())