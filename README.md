# MirrorManager

the goal of mirrormanager is to allow for easy setup of hosting file mirrors, with the added benefit of a simple file-browser, downloader and file searcher

## Installation
at the moment mirrormanger only supports freebsd, hardenedbsd and any other bsd operating systems based upon freebsd.  
technically it should be able to run on any os, freebsd is just preferred since the download scripts are configured for pkg.  
also highly recommend installing mm into a freebsd jail. if you are unfamiliar with using jails try http://github.com/bsdpot/pot  

to install mirrormanager you'll need
- python3.10 or higher (py3.11 recommended)
- freebsd
- at least 20gb of disk (file mirrors take up a lot of space!)
- git
- uvicorn

1. install python and pip  
   - ``cd /tmp``  
   - ``pkg install python311 curl``  
   - ``curl -O -L https://bootstrap.pypa.io/get-pip.py``  
   - ``python3.11 get-pip.py``  

2. setup mirrormanager  
   - ``cd /usr/local/etc/mirrormanger``  
   - ``git clone https://ttea.dev/t2v/mm . --depth-1``  
   - ``pip install -r requirements.txt --upgrade``   
  
3. configure mirrors
   - ``ee /usr/local/etc/mirrormanger/configs/mirrors.json``
   - follow the format of the examples in the config file
   - run the setup and validation script (this NEEDS to be run after every edit of mirrors.json)
   - ``/usr/local/bin/python3.11 /usr/local/etc/mirrormanager/setup.py`` 
   - follow any instructions from the setup script

4. start mirrormanager   
- from terminal  
    - using python (recommended)  
        ``/usr/local/bin/python3.11 /usr/local/etc/mirrormanager/main.py``  
        - will run on host 0.0.0.0 and port 8000  
    - using uvicorn directly  
        ``/usr/local/bin/python3.11 /usr/local/bin/uvicorn main:app --host 0.0.0.0 --port 8000``  
        - change host and port to your liking  
- using bsd rc  
    - coming soon  

## Development
NOTE: This project uses `black` as its code formatter.
