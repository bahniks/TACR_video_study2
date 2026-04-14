from __future__ import annotations

import getpass
import hmac
import os
import sys
import tempfile
import tkinter as tk
import zipfile

from hashlib import pbkdf2_hmac, sha256
from pathlib import Path
from tkinter import messagebox, simpledialog


MAGIC = b"TACROBF1"
SALT_SIZE = 16
NONCE_SIZE = 16
MAC_SIZE = 32
CHUNK_SIZE = 1024 * 1024
PBKDF2_ITERATIONS = 200_000

SCRIPT_DIR = Path(__file__).resolve().parent
DISTRACTIONS_DIR = SCRIPT_DIR / "Distractions"
VIDEO_OBFS = ["videos1.obf", "videos2.obf"]


def should_use_gui() -> bool:
    executable_name = Path(sys.executable).name.lower()
    return executable_name == "pythonw.exe" or not sys.stdin.isatty() or not sys.stdout.isatty()


class GuiSession:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.withdraw()

    def ask_password(self) -> str:
        password = simpledialog.askstring(
            "Restore distractions",
            "Enter password to restore distractions:",
            parent=self.root,
        )
        if password is None:
            raise ValueError("Installation cancelled.")
        if not password:
            raise ValueError("Password cannot be empty.")
        return password

    def show_error(self, message: str) -> None:
        messagebox.showerror("Restore distractions", message, parent=self.root)

    def show_info(self, message: str) -> None:
        messagebox.showinfo("Restore distractions", message, parent=self.root)

    def close(self) -> None:
        self.root.destroy()


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


def ensure_only_obfuscated_files_present() -> None:
    if not DISTRACTIONS_DIR.is_dir():
        raise FileNotFoundError(f"Distractions directory not found: {DISTRACTIONS_DIR}")

    entries = sorted(item.name for item in DISTRACTIONS_DIR.iterdir())
    if entries != VIDEO_OBFS:
        raise RuntimeError(
            "Distractions must contain only the obfuscated files before installation. "
            f"Found: {', '.join(entries) if entries else 'nothing'}"
        )


def restore_archive(obfuscated_file: Path, restored_zip: Path, password: str) -> None:
    file_size = obfuscated_file.stat().st_size
    header_size = len(MAGIC) + SALT_SIZE + NONCE_SIZE
    minimum_size = header_size + MAC_SIZE

    if file_size <= minimum_size:
        raise ValueError("Obfuscated file is too small or invalid.")

    temp_path: Path | None = None
    counter = 0

    try:
        with obfuscated_file.open("rb") as source_file:
            magic = source_file.read(len(MAGIC))
            if magic != MAGIC:
                raise ValueError("Unrecognized obfuscated file format.")

            salt = source_file.read(SALT_SIZE)
            nonce = source_file.read(NONCE_SIZE)
            encryption_key, mac_key = derive_keys(password, salt)

            authenticator = hmac.new(mac_key, digestmod="sha256")
            authenticator.update(magic + salt + nonce)

            encrypted_bytes_remaining = file_size - header_size - MAC_SIZE

            with tempfile.NamedTemporaryFile(delete=False, dir=DISTRACTIONS_DIR, suffix=".tmp") as temp_file:
                temp_path = Path(temp_file.name)

                while encrypted_bytes_remaining > 0:
                    chunk = source_file.read(min(CHUNK_SIZE, encrypted_bytes_remaining))
                    if not chunk:
                        raise ValueError("Unexpected end of obfuscated file.")

                    encrypted_bytes_remaining -= len(chunk)
                    authenticator.update(chunk)
                    transformed_chunk, counter = transform_chunk(chunk, encryption_key, nonce, counter)
                    temp_file.write(transformed_chunk)

                stored_mac = source_file.read(MAC_SIZE)
                if len(stored_mac) != MAC_SIZE:
                    raise ValueError("Missing integrity checksum.")

            calculated_mac = authenticator.digest()
            if not hmac.compare_digest(calculated_mac, stored_mac):
                raise ValueError("Incorrect password or corrupted obfuscated file.")

        os.replace(temp_path, restored_zip)
    except Exception:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()
        raise


def extract_archive(zip_file: Path) -> None:
    destination = DISTRACTIONS_DIR.resolve()

    with zipfile.ZipFile(zip_file, "r") as archive:
        for member in archive.infolist():
            member_path = (destination / member.filename).resolve()
            if member_path != destination and destination not in member_path.parents:
                raise ValueError(f"Archive contains an invalid path: {member.filename}")

        archive.extractall(destination)

    zip_file.unlink()


def run_install(password: str) -> None:
    ensure_only_obfuscated_files_present()
    for obf_name in VIDEO_OBFS:
        obfuscated_file = DISTRACTIONS_DIR / obf_name
        restored_zip = DISTRACTIONS_DIR / obf_name.replace(".obf", ".zip")
        restore_archive(obfuscated_file, restored_zip, password)
        extract_archive(restored_zip)


def main() -> int:
    gui_session = GuiSession() if should_use_gui() else None

    try:
        if gui_session is None:
            password = getpass.getpass("Enter password to restore distractions: ")
            if not password:
                raise ValueError("Password cannot be empty.")
        else:
            password = gui_session.ask_password()

        run_install(password)
    except Exception as exc:
        if gui_session is None:
            print(f"Error: {exc}", file=sys.stderr)
        else:
            gui_session.show_error(str(exc))
            gui_session.close()
        return 1

    if gui_session is None:
        print("Distractions restored and extracted.")
    else:
        gui_session.show_info("Distractions restored and extracted.")
        gui_session.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())