#!python
import requests
import re
import os
import tarfile
from distutils.version import StrictVersion
import time


class TorProject:
    """Class to perform operations on the TorProject site"""

    tor_project_root = "https://www.torproject.org"
    downloads_page = tor_project_root + "/download/"
    
    """
    	GET /torbrowser/11.0.14/tor-browser-linux64-11.0.14_en-US.tar.xz HTTP/1.1
	Host: dist.torproject.org
	User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:101.0) Gecko/20100101 Firefox/101.0
	Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
	Accept-Language: en-GB,en;q=0.5
	Accept-Encoding: gzip, deflate, br
	Connection: keep-alive
	Upgrade-Insecure-Requests: 1
	Sec-Fetch-Dest: document
	Sec-Fetch-Mode: navigate
	Sec-Fetch-Site: none
	Sec-Fetch-User: ?1
    """

    headers = {
        # 'Host': 'dist.torproject.org',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:101.0) Gecko/20100101 Firefox/101.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-GB,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
	'Sec-Fetch-Mode': 'navigate',
	'Sec-Fetch-Site': 'none',
	'Sec-Fetch-User': '?1'
    }

    def __init__(self):
        print(f"Getting {self.downloads_page}")
        with requests.get(self.downloads_page, timeout=1) as r:
            r.raise_for_status()
            print("Page has been downloaded")

            # This is an example of what we want the regexp to find
            # href="/dist/torbrowser/9.0.1/tor-browser-linux64-9.0.1_en-US.tar.xz"
            # href="/dist/torbrowser/10.0/tor-browser-linux64-10.0_en-US.tar.xz
            # href="/dist/torbrowser/10.0.10/tor-browser-linux64-10.0.10_en-US.tar.xz
            re_download_link = (
                r"""href="(/dist/torbrowser/(\d+\.\d+\.?\d*?)/tor.+tar.xz)"""
            )
            m = re.search(re_download_link, r.text)
            if m:
                self.download_url = self.tor_project_root + m.group(1)
                self.latest_version = m.group(2)
            else:
                print(r.text)
                raise ValueError("Could not find download link")

    def download_latest(self):
        time.sleep(5)
        print(self.download_url)
        print(self.headers)
        local_filename = self.download_url.split("/")[-1]

        with requests.get(self.download_url, stream=True, headers=self.headers, timeout=5) as r:
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
    toml_file = folder + "/tor-browser/start-tor-browser.desktop"
    with open(toml_file, "r") as f:
        for line in f:
            m = re.search(r"""Exec=(.+)$""", line)
            if m:
                print(m.group(1))
                os.chdir(folder + "/tor-browser")
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
