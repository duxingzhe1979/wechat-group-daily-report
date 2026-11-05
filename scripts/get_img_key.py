# -*- coding: utf-8 -*-
"""Deterministically derive the WeChat 4.x image AES key (no memory scan).

AES key = md5(f"{code}{wxid}")[:16]  (16-char ASCII hex)
XOR key = code & 0xFF
`code` comes from the filename of key_<code>_*.statistic under
%APPDATA%/Tencent/xwechat/net/kvcomm/.

Verified against real encrypted thumbnails: decrypt the first AES block of a
recent *_t.dat and require a real image magic (jpeg/png/webp/wxgf/gif).
Output: img_key.txt next to this script ("aes_key\\nxor_dec").
"""
import hashlib
import os
import re
import struct
import sys
from collections import Counter

from Crypto.Cipher import AES

APPDATA = os.environ.get("APPDATA", os.path.expanduser("~/AppData/Roaming"))
KVCOMM_DIRS = [
    os.path.join(APPDATA, "Tencent", "xwechat", "net", "kvcomm"),
]
ACC_ROOT = os.path.expanduser("~/Documents/xwechat_files")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img_key.txt")

V2_MAGIC = bytes((0x07, 0x08, 0x56, 0x32, 0x08, 0x07))
START = 0x0F
KEY_RE = re.compile(r"^key_(\d+)_", re.I)


def codes_from_kvcomm():
    codes = set()
    for d in KVCOMM_DIRS:
        if not os.path.isdir(d):
            continue
        for fn in os.listdir(d):
            m = KEY_RE.match(fn)
            if m:
                codes.add(int(m.group(1)))
    return sorted(codes)


def accounts():
    if not os.path.isdir(ACC_ROOT):
        return []
    return [os.path.join(ACC_ROOT, d) for d in os.listdir(ACC_ROOT)
            if d.startswith("wxid_") and os.path.isdir(os.path.join(ACC_ROOT, d))]


def clean_wxid(name):
    m = re.fullmatch(r"(wxid_[^_]+)(?:_.+)?", name)
    return m.group(1) if m else name


def templates(account_dir, limit=16):
    """Recent encrypted thumbnail first-blocks: [(ciphertext16, path)]"""
    root = os.path.join(account_dir, "msg", "attach")
    files = []
    for dp, _, fns in os.walk(root):
        if os.path.basename(dp).lower() != "img":
            continue
        for fn in fns:
            if fn.lower().endswith("_t.dat"):
                p = os.path.join(dp, fn)
                try:
                    files.append((os.stat(p).st_mtime_ns, p))
                except OSError:
                    pass
    files.sort(reverse=True)
    out = []
    for _, p in files[: limit * 4]:
        try:
            with open(p, "rb") as f:
                head = f.read(START + 16)
            if len(head) == START + 16 and head.startswith(V2_MAGIC):
                out.append((head[START:], p))
        except OSError:
            continue
        if len(out) >= limit:
            break
    return out


def sniff(pt):
    if pt.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if pt.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if pt.startswith(b"RIFF") and pt[8:12] == b"WEBP":
        return "webp"
    if pt.startswith((b"wxgf", b"WXGF")):
        return "wxgf"
    if pt.startswith((b"GIF87a", b"GIF89a")):
        return "gif"
    return None


def main():
    codes = codes_from_kvcomm()
    if not codes:
        sys.exit("no kvcomm key_*.statistic files found")
    accs = accounts()
    if not accs:
        sys.exit("no xwechat_files account dirs found")
    for acc in accs:
        wxid = clean_wxid(os.path.basename(acc))
        tpls = templates(acc)
        if not tpls:
            print(f"{wxid}: no V2 thumbnails, skip")
            continue
        for code in codes:
            key = hashlib.md5(f"{code}{wxid}".encode()).hexdigest()[:16]
            hits = Counter()
            for ct, _ in tpls:
                try:
                    pt = AES.new(key.encode(), AES.MODE_ECB).decrypt(ct)
                except ValueError:
                    break
                f = sniff(pt)
                if f:
                    hits[f] += 1
            if hits:
                xor = code & 0xFF
                print(f"[+] wxid={wxid} code={code} aes_key={key} xor=0x{xor:02X} "
                      f"verified={dict(hits)}/{len(tpls)}")
                with open(OUT, "w") as f:
                    f.write(f"{key}\n{xor}\n")
                return
        print(f"{wxid}: no code matched ({len(codes)} codes tried, {len(tpls)} templates)")
    sys.exit("image key derivation failed")


if __name__ == "__main__":
    main()
