"""Inspect collected files without executing third-party code or importing into Godot."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import struct
import zipfile


ROOT = Path(__file__).resolve().parents[2]
LIBRARY = ROOT / "local_assets" / "bang_dream"


def inspect_glb(path: Path) -> dict:
    data = path.read_bytes()
    assert len(data) >= 20, "GLB too short"
    magic, version, length = struct.unpack_from("<4sII", data)
    assert (magic, version, length) == (b"glTF", 2, len(data)), "Invalid GLB header"
    offset, chunks = 12, []
    while offset < length:
        assert offset + 8 <= length, "Truncated chunk header"
        size, kind = struct.unpack_from("<II", data, offset)
        offset += 8
        assert size % 4 == 0 and offset + size <= length, "Invalid chunk length"
        chunks.append((kind, data[offset:offset + size]))
        offset += size
    assert chunks[0][0] == 0x4E4F534A, "Missing JSON chunk"
    doc = json.loads(chunks[0][1])
    assert doc["asset"]["version"] == "2.0"
    assert len(chunks) == 2 and chunks[1][0] == 0x004E4942, "Expected embedded BIN"
    assert len(doc.get("buffers", [])) == 1 and "uri" not in doc["buffers"][0]
    assert doc["buffers"][0]["byteLength"] <= len(chunks[1][1])
    for view in doc.get("bufferViews", []):
        assert view["buffer"] == 0
        assert view.get("byteOffset", 0) + view["byteLength"] <= doc["buffers"][0]["byteLength"]
    for image in doc.get("images", []):
        assert "uri" not in image, "External image needs separate collection"
        assert 0 <= image["bufferView"] < len(doc["bufferViews"])
    nodes = doc.get("nodes", [])
    for skin in doc.get("skins", []):
        assert all(0 <= joint < len(nodes) for joint in skin["joints"])
    return {
        "format": "glTF 2.0 binary",
        "bytes": len(data),
        "meshes": len(doc.get("meshes", [])),
        "materials": len(doc.get("materials", [])),
        "skins": len(doc.get("skins", [])),
        "joint_counts": [len(s["joints"]) for s in doc.get("skins", [])],
        "animations": len(doc.get("animations", [])),
        "embedded_images": len(doc.get("images", [])),
        "generator": doc["asset"].get("generator"),
    }


def main() -> None:
    catalog = json.loads((LIBRARY / "catalog.json").read_text())
    result = {"characters_requested": len(catalog["characters"]), "collected": [], "pending": []}
    for character in catalog["characters"]:
        if not character["files"]:
            assert character["status"] != "downloaded"
            result["pending"].append(character["name_zh"])
            continue
        record = {"character": character["name_zh"], "files": []}
        for item in character["files"]:
            path = (LIBRARY / item["path"]).resolve()
            assert path.is_relative_to(LIBRARY.resolve()), "Path escapes library"
            assert path.is_file(), f"Missing: {path.name}"
            assert path.stat().st_size == item["bytes"], "File size mismatch"
            assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"], "SHA256 mismatch"
            details = {"path": item["path"], "sha256_verified": True}
            if path.suffix.lower() == ".zip":
                with zipfile.ZipFile(path) as archive:
                    assert archive.testzip() is None, "Archive CRC failed"
                    details["entries"] = [{"name": i.filename, "bytes": i.file_size} for i in archive.infolist()]
            elif path.suffix.lower() == ".glb":
                details.update(inspect_glb(path))
            record["files"].append(details)
        result["collected"].append(record)
    report = LIBRARY / "reports" / "file_audit.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"FILE_AUDIT_COMPLETE: {len(result['collected'])} collected, {len(result['pending'])} pending")


if __name__ == "__main__":
    main()
