import sys
import os
import json
import shutil
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PKG_DIR = os.path.join(BASE_DIR, "packages")
CACHE_DIR = os.path.join(PKG_DIR, "cache")
COMMUNITY_HUB_DIR = os.path.join(BASE_DIR, "community_hub")
INDEX_FILE = os.path.join(COMMUNITY_HUB_DIR, "hub_index.json")

def ensure_dirs():
    if not os.path.exists(PKG_DIR):
        os.makedirs(PKG_DIR)
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
    if not os.path.exists(COMMUNITY_HUB_DIR):
        os.makedirs(COMMUNITY_HUB_DIR)
    if not os.path.exists(INDEX_FILE):
        default_index = {
            "version": "1.0.0",
            "packages": {
                "packet_utils": {
                    "version": "1.0.0",
                    "author": "TrappyCore",
                    "description": "Utilities for building and parsing formatted network packets",
                    "file": "packet_utils.trappy"
                },
                "physics_2d": {
                    "version": "1.15.0",
                    "author": "TrappyGames",
                    "description": "Standard 2D velocity, gravity calculation, and box bounce physics",
                    "file": "physics_2d.trappy"
                },
                "chat_client": {
                    "version": "1.0.0",
                    "author": "CommunityApp",
                    "description": "A reusable network messaging and client interaction module",
                    "file": "chat_client.trappy"
                }
            }
        }
        with open(INDEX_FILE, "w", encoding="utf-8") as f:
            json.dump(default_index, f, indent=4)

def load_index():
    ensure_dirs()
    try:
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"packages": {}}

def save_index(data):
    ensure_dirs()
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def list_installed():
    ensure_dirs()
    pkgs = [f for f in os.listdir(PKG_DIR) if f.endswith(".trappy")]
    print("\nInstalled Packages in /packages:")
    if not pkgs:
        print("  (No packages installed yet. Use 'tpm search' to find packages.)")
    for p in pkgs:
        print(f"  * {p}")
    print()

def search_hub(keyword=""):
    index = load_index()
    pkgs = index.get("packages", {})
    print(f"\nTrappy Community Hub Search: '{keyword}'")
    print("-" * 65)
    matched = 0
    for name, info in pkgs.items():
        desc = info.get("description", "")
        author = info.get("author", "Anonymous")
        ver = info.get("version", "0.1")
        if not keyword or keyword.lower() in name.lower() or keyword.lower() in desc.lower():
            print(f"  * {name:<16} [v{ver}] by {author}")
            print(f"    {desc}")
            matched += 1
    if matched == 0:
        print("  No community packages found matching that keyword.")
    print("-" * 65)
    print(f"Total: {matched} package(s) found. Run 'tpm install <name>' to install.\n")

def install_package(pkg_name_or_url):
    ensure_dirs()
    if pkg_name_or_url.startswith("http://") or pkg_name_or_url.startswith("https://"):
        target_name = pkg_name_or_url.split("/")[-1]
        if not target_name.endswith(".trappy"):
            target_name += ".trappy"
        target_path = os.path.join(PKG_DIR, target_name)
        print(f"Downloading package from: {pkg_name_or_url} ...")
        try:
            req = urllib.request.Request(pkg_name_or_url, headers={'User-Agent': 'TPM/0.9'})
            with urllib.request.urlopen(req, timeout=15) as resp:
                content = resp.read()
            with open(target_path, "wb") as f:
                f.write(content)
            print(f"Successfully installed '{target_name}' into /packages.")
        except Exception as e:
            print(f"Failed to download package: {e}")
        return

    index = load_index()
    pkgs = index.get("packages", {})
    clean_name = pkg_name_or_url.replace(".trappy", "")
    if clean_name in pkgs:
        info = pkgs[clean_name]
        src_file = os.path.join(COMMUNITY_HUB_DIR, info["file"])
        dest_file = os.path.join(PKG_DIR, f"{clean_name}.trappy")
        if os.path.exists(src_file):
            shutil.copyfile(src_file, dest_file)
            print(f"Successfully installed community package '{clean_name}' (v{info.get('version')}) into /packages.")
        else:
            print(f"Package '{clean_name}' entry found, but package file is missing in hub.")
    else:
        print(f"Package '{pkg_name_or_url}' not found in community hub. Use 'tpm search' to list available packages.")

def publish_package(filepath, author="Community", description="A community Trappy package"):
    ensure_dirs()
    if not os.path.exists(filepath):
        print(f"Cannot publish: file '{filepath}' does not exist.")
        return

    filename = os.path.basename(filepath)
    if not filename.endswith(".trappy"):
        print("Only .trappy files can be published to the Trappy Community Hub.")
        return

    pkg_name = filename[:-7]
    hub_dest = os.path.join(COMMUNITY_HUB_DIR, filename)
    shutil.copyfile(filepath, hub_dest)

    index = load_index()
    index["packages"][pkg_name] = {
        "version": "1.0.0",
        "author": author,
        "description": description,
        "file": filename
    }
    save_index(index)
    print(f"Successfully published '{pkg_name}' to Trappy Community Hub!")
    print(f"  Author: {author}")
    print(f"  Description: {description}")
    print(f"  Others can now install it using: tpm install {pkg_name}\n")

if __name__ == "__main__":
    ensure_dirs()
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help", "help"):
        print("\nTrappy Package Manager & Community Hub (TPM v0.9)")
        print("Usage:")
        print("  tpm list                             List installed packages")
        print("  tpm search [keyword]                 Search community packages in hub")
        print("  tpm install <name_or_url>            Download and install a package")
        print("  tpm publish <file.trappy> [author]   Publish an app/package for others")
        print()
    elif args[0] == "list":
        list_installed()
    elif args[0] == "search":
        kw = args[1] if len(args) > 1 else ""
        search_hub(kw)
    elif args[0] == "install":
        if len(args) > 1:
            install_package(args[1])
        else:
            print("Please provide package name. Example: tpm install physics_2d")
    elif args[0] == "publish":
        if len(args) > 1:
            target_path = args[1]
            author = args[2] if len(args) > 2 else "Community"
            desc = " ".join(args[3:]) if len(args) > 3 else "A community Trappy creation"
            publish_package(target_path, author, desc)
        else:
            print("Usage: tpm publish <file.trappy> [author] [description]")
    elif args[0] == "discord":
        print("\nTrappy Official Community Headquarters:")
        print("  Discord: https://discord.gg/3chDfAPE9H")
        print("  Share packages, request help, showcase games, and collaborate with creators!\n")
    else:
        print(f"Unknown command: '{args[0]}'. Run 'tpm help' for usage.")
