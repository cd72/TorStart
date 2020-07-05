#!python
import requests
import re
import os
import tarfile
from distutils.version import StrictVersion


class TorProject:
    """Class to perform operations on the TorProject site"""

    tor_project_root = "https://www.torproject.org"
    downloads_page = tor_project_root + "/download/"

    def __init__(self):
        with requests.get(self.downloads_page) as r:
            r.raise_for_status()

            # This is an example of what we want the regexp to find
            # href="/dist/torbrowser/9.0.1/tor-browser-linux64-9.0.1_en-US.tar.xz"
            re_download_link = (
                r"""href="(/dist/torbrowser/(\d\.\d\.?\d?)/tor.+tar.xz)"""
            )
            m = re.search(re_download_link, r.text)
            if m:
                self.download_url = self.tor_project_root + m.group(1)
                self.latest_version = m.group(2)
            else:
                raise ValueError("Could not find download link")

    def download_latest(self):
        local_filename = self.download_url.split("/")[-1]
        with requests.get(self.download_url, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, "wb") as f:
                for chunk in r.iter_content(chunk_size=1048576):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
                        print(".", end="", flush=True)
                        # f.flush()
        print()
        return local_filename


def get_current_tor_version():
    with open("current_tor_version.txt", "r") as f:
        current_tor_version = f.read().rstrip()
        return current_tor_version


def write_current_tor_version(version_string):
    with open("current_tor_version.txt", "w") as f:
        f.write(version_string)


def install_new_version_from_xz(folder, xz_file):
    print("Extracting")
    with tarfile.open(xz_file) as f:
        f.extractall(folder)


def launch_tor(folder):
    # we started off with importing toml module but found that the .desktop file
    # had invalid toml - due to spaces in a  non-quoted tag
    toml_file = folder + "/tor-browser_en-US/start-tor-browser.desktop"
    with open(toml_file, "r") as f:
        for line in f:
            m = re.search(r"""Exec=(.+)$""", line)
            if m:
                print(m.group(1))
                os.chdir(folder + "/tor-browser_en-US")
                os.system(m.group(1))


def main():
    current_tor_version = get_current_tor_version()
    print(f"Current tor version is {current_tor_version}!")

    tor_project = TorProject()
    print(f"Latest tor version is {tor_project.latest_version}!")

    if StrictVersion(current_tor_version) < StrictVersion(tor_project.latest_version):
        print("Downloading new version")
        download_file = tor_project.download_latest()
        install_new_version_from_xz(tor_project.latest_version, download_file)
        write_current_tor_version(tor_project.latest_version)

    print(f"Launching tor with {tor_project.latest_version}")
    launch_tor(tor_project.latest_version)


if __name__ == "__main__":
    main()
