import os
import sys
import subprocess
import pkg_resources
from importlib import import_module
import importlib
import platform


def check_req_packages(packages, show_package_info=False):
    checking_package = ""
    try:
        for package in packages:
            # print(package)
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
                # print(package, checking_package)
                importlib.reload(import_module(package))
                if "==" in packages[package]:
                    temp = packages[package].split("==")
                    importlib.reload(pkg_resources)
                    version = pkg_resources.get_distribution(temp[0]).version
                    if version != temp[1]:
                        # print(show_package_info, flush=True)
                        if show_package_info:
                            print(f"Name: {package}; Current: {version}; Need: {temp[1]}", flush=True)
                        raise ModuleNotFoundError

        for package in packages:
            print(f"{package} is ok :)", flush=True)
    except FileNotFoundError:
        print(f"{checking_package} is not ok :(", flush=True)
        print(f"I will try to install this automatically.", flush=True)
        if checking_package == "ffmpeg":
            ffdl_downl = subprocess.run([sys.executable, "-m", "pip", "install", "ffmpeg-downloader", "--no-cache-dir"],
                                        capture_output=True, text=True)
            # print(ffdl_downl.stdout)
            # print(ffdl_downl.stderr)
            ffdl = subprocess.run(["ffdl", "install", "-y"], capture_output=True, text=True)
            # print(ffdl.stdout)
            # print(ffdl.stderr)
        check_req_packages(packages, show_package_info)
    except (ModuleNotFoundError, ImportError):
        print(f"{checking_package} is not ok :(", flush=True)
        print(f"I will try to install this automatically.", flush=True)
        if platform.system() == "Linux":
            subprocess.run(["sudo", sys.executable, "-m", "pip", "install", packages[checking_package], "--no-cache-dir"],
                           capture_output=True, text=True)
        else:
            subprocess.run([sys.executable, "-m", "pip", "install", packages[checking_package], "--no-cache-dir"],
                           capture_output=True, text=True)
        check_req_packages(packages, show_package_info)
