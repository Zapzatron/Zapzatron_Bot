import os
import sys
import subprocess
import pkg_resources
from importlib import import_module


def check_req_packages(packages):
    checking_package = ""
    try:
        for package in packages:
            checking_package = package
            if package == "ffmpeg":
                try:
                    ffdl = import_module("ffmpeg_downloader")
                    ffmpeg_path = ffdl.ffmpeg_dir
                    if ffmpeg_path not in os.environ['PATH'].split(os.pathsep):
                        os.environ['PATH'] += os.pathsep + ffmpeg_path
                except ModuleNotFoundError:
                    pass
                subprocess.run([package], capture_output=True, text=True)
            else:
                import_module(package)
                if "==" in packages[package]:
                    temp = packages[package].split("==")
                    version = pkg_resources.get_distribution(temp[0]).version
                    # print(version, temp[1])
                    if version != temp[1]:
                        raise ModuleNotFoundError

        for package in packages:
            print(f"{package} is ok :)")
    except FileNotFoundError:
        print(f"{checking_package} is not ok :(")
        print(f"I will try to install this automatically.")
        if checking_package == "ffmpeg":
            ffdl_downl = subprocess.run([sys.executable, "-m", "pip", "install", "ffmpeg-downloader", "--no-cache-dir"], capture_output=True, text=True)
            # print(ffdl_downl.stdout)
            # print(ffdl_downl.stderr)
            ffdl = subprocess.run(["ffdl", "install", "-y"], capture_output=True, text=True)
            # print(ffdl.stdout)
            # print(ffdl.stderr)
        check_req_packages(packages)
    except ModuleNotFoundError:
        print(f"{checking_package} is not ok :(")
        print(f"I will try to install this automatically.")
        subprocess.run([sys.executable, "-m", "pip", "install", packages[checking_package], "--no-cache-dir"], capture_output=True, text=True)
        check_req_packages(packages)
