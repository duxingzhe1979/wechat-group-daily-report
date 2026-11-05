# -*- coding: utf-8 -*-
"""Batch-decrypt WeChat 4.x V2 image .dat files (open-source edition).

V2 layout: 15-byte header (magic 0708 5632 0807 + aes_len@6 + xor_len@10),
then AES-128-ECB over `(aes_len & ~0xF) + 16` bytes, then single-byte XOR
over the remainder. The AES key is *not* hardcoded — it is derived from
`%APPDATA%/Tencent/xwechat/net/kvcomm/` via get_img_key.py (md5(code+wxid))
and cached in img_key.txt next to this script.

Accounts and chat dirs are auto-discovered from ~/Documents/xwechat_files/.
Output sniffed: jpeg/png/webp/gif written directly, wxgf decoded to PNG
via PyAV. Usage:  python decrypt_wechat_images.py [YYYY-MM]
"""
import glob
import hashlib
import os
import struct
import sys
from Crypto.Cipher import AES

try:
    import av  # wxgf decode
except ImportError:
    av = None

START = 0x0F
V2_MAGIC = bytes((0x07, 0x08, 0x56, 0x32, 0x08, 0x07))
HERE = os.path.dirname(os.path.abspath(__file__))
OUTROOT = os.path.join(HERE, "imgs_ok")
KEY_FILE = os.path.join(HERE, "img_key.txt")
MONTH = sys.argv[1] if len(sys.argv) > 1 else None  # None -> latest month dir found


def load_key():
    """Return (key_bytes, xor_int); derive via get_img_key.py when missing."""
    if os.path.isfile(KEY_FILE):
        lines = open(KEY_FILE).read().split()
        if len(lines) >= 2:
            return lines[0].encode(), int(lines[1])
    print("[*] img_key.txt not found, deriving via get_img_key.py ...")
    import get_img_key
    try:
        get_img_key.main()
    except SystemExit as e:
        sys.exit(f"key derivation failed: {e}")
    lines = open(KEY_FILE).read().split()
    return lines[0].encode(), int(lines[1])


def attach_roots():
    home = os.path.expanduser("~")
    return sorted(glob.glob(os.path.join(home, "Documents", "xwechat_files", "wxid_*", "msg", "attach")))


def month_dirs():
    """Yield (chat_dir_path, month) pairs to process."""
    for root in attach_roots():
        for chat in sorted(os.listdir(root)):
            cpath = os.path.join(root, chat)
            if not os.path.isdir(cpath):
                continue
            for ym in sorted(os.listdir(cpath)):
                if ym[:4] != "20":
                    continue
                if MONTH and ym != MONTH:
                    continue
                yield os.path.join(cpath, ym, "Img"), f"{chat}_{ym}"


def sniff(pt):
    if pt.startswith(b"\xff\xd8\xff"):
        return "jpg", pt
    if pt.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png", pt
    if pt.startswith(b"RIFF") and pt[8:12] == b"WEBP":
        return "webp", pt
    if pt.startswith((b"GIF87a", b"GIF89a")):
        return "gif", pt
    if pt.startswith((b"wxgf", b"WXGF")):
        return "wxgf", pt
    return None, pt


def decrypt_file(src, key, xor):
    with open(src, "rb") as f:
        raw = f.read()
    if len(raw) <= START + 16 or not raw.startswith(V2_MAGIC):
        return None
    aes_len = struct.unpack("<I", raw[6:10])[0]
    n = (aes_len & ~0xF) + 16  # AES region covers one extra block past aligned aes_len
    body = raw[START:]
    if n > len(body):
        n = len(body) & ~0xF
    try:
        pt = AES.new(key, AES.MODE_ECB).decrypt(body[:n]) + bytes(b ^ xor for b in body[n:])
    except ValueError:
        return None
    return pt


def wxgf_to_png(payload):
    """wxgf = Annex-B HEVC starting at the first 00 00 00 01 start code."""
    if av is None:
        return None
    import io
    import av
    idx = payload.find(b"\x00\x00\x00\x01")
    if idx < 0:
        return None
    try:
        container = av.open(io.BytesIO(payload[idx:]))
        for frame in container.decode(video=0):
            buf = io.BytesIO()
            frame.to_image().save(buf, format="PNG")
            return buf.getvalue()
    except Exception:
        return None
    return None


def main():
    key, xor = load_key()
    print(f"[*] aes_key={key.decode()} xor=0x{xor:02X}")
    ok = fail = 0
    for imgdir, tag in month_dirs():
        if not os.path.isdir(imgdir):
            continue
        outdir = os.path.join(OUTROOT, tag)
        os.makedirs(outdir, exist_ok=True)
        for fn in sorted(os.listdir(imgdir)):
            if not fn.endswith(".dat"):
                continue
            src = os.path.join(imgdir, fn)
            pt = decrypt_file(src, key, xor)
            if pt is None:
                fail += 1
                continue
            kind, data = sniff(pt)
            if kind == "wxgf":
                png = wxgf_to_png(pt)
                if png:
                    kind, data = "png", png
                else:
                    fail += 1
                    continue
            elif kind is None:
                fail += 1
                continue
            base = os.path.splitext(fn)[0]
            with open(os.path.join(outdir, f"{base}.{kind}"), "wb") as f:
                f.write(data)
            ok += 1
    print(f"[+] done: {ok} ok, {fail} failed/skipped -> {OUTROOT}")


if __name__ == "__main__":
    main()
