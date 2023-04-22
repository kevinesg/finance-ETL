# finance-etl

1. generate SSH keys
    - go to [https://cloud.google.com/compute/docs/connect/create-ssh-keys](https://cloud.google.com/compute/docs/connect/create-ssh-keys) for instructions
    - as mentioned in the docs, input `ssh-keygen -t rsa -f ~/.ssh/KEY_FILENAME -C USERNAME -b 2048` into your linux terminal or bash (change `KEY_FILENAME` and `USERNAME` to whatever you want)
    - assigning password is optional (just click enter)
    - `cd ~/.ssh`
    - `ls`
    - you should see the two ssh keys (one public and one private)
    - these keys will be used to access the VM in the later steps

2. create a GCP project
    - create an account on `cloud.google.com`
    - go to `IAM & Admin`>`Create a Project` to create a dedicated project for this ETL

3. add the SSH key
    - make sure you are in the correct project (check upper left of the web page)
    - go to `Compute Engine` > `Settings`>`Metadata`
    - click `SSH KEYS` tab then `ADD SSH KEY`
    - go back to your linux terminal or bash, then `cd ~/.ssh`
    - `cat KEY_FILENAME.pub` (use your KEY_FILENAME) to view the contents of the public key
    - copy and paste the contents into the text field of SSH key then click save
    - this public SSH key will now be used by all instances in this project (including VMs)

4. create a GCP VM
    - go to `Compute Engine` then `VM instances`
    - you might need to click `enable service` on the required API first
    - click `CREATE INSTANCE`
    - as for the details of the VM, you can refer to this [youtube video](https://www.youtube.com/watch?v=tcPdin9cf4w) if you prefer to use a free VM
    - under `Boot disk`, click `CHANGE` and choose your preferred OS and version (I chose Ubuntu 22.04 LTS (x86/64)). you can also adjust the size (I chose 30 GB)
    - after finalizing all VM specifications, click `SELECT` then wait for the VM instance to run

5. SSH into the VM
    - click the three dots (more actions) then `View network details`, take note of the `External IP address` value
    - in your linux terminal or bash, type `ssh -i ~/.ssh/KEY_FILENAME USERNAME@EXTERNAL_IP_ADDRESS` (use your `KEY_FILENAME` and `USERNAME` from the previous steps, then `EXTERNAL_IP_ADDRESS` from the VM)
    - you should have successfully entered your GCP VM
    - you can exit out of the VM by entering `logout`
    - create a config file in ~/.ssh (optional but recommended)

        - in this step, we will create a shortcut to SSH into the VM (so we don't have to enter `ssh -i ~/.ssh/KEY_FILENAME USERNAME@EXTERNAL_IP_ADDRESS` every time)
        - in your local linux terminal or bash, `cd ~/.ssh` then `touch config`
        - `code config` (if you have `VS Code` installed) or `nano config` to edit the config file
        - enter the following lines

                Host NAME
                Hostname EXTERNAL_IP_ADDRESS
                User USERNAME
                IdentityFile ~/.ssh/PRIVATE_SSH_KEY
        
            where 

            - `NAME` is the name you want to use in the command `ssh NAME` to SSH into the VM
            - `EXTERNAL_IP_ADDRESS` and `USERNAME` are from previous steps
            - `PRIVATE_SSH_KEY` is the file name of the private SSH key we created in step 3
            - in windows, you might need to enter the absolute path instead of relative path for the IdentityFile

        - save changes to `config`
        - now you can SSH into the VM by just using `ssh NAME` (where `NAME` is what you entered in `config`). unfortunately, whenever you stop the GCP VM, once you start it again, you have to update `EXTERNAL_IP_ADDRESS`

6. configure VM
    - note: the following steps are only applicable for Ubuntu VMs. you might need to tweak it a little bit for other OS
    - install `Anaconda` (or `Miniconda`)

        - `Miniconda` is basically the same as `Anaconda` except there's no built-in packages when you create a new conda environment. feel free to choose either of the two
        - download `Anaconda` installer from the [official site](https://www.anaconda.com/download/) (or [here](https://docs.conda.io/en/latest/miniconda.html) for `Miniconda`). scroll down to the bottom of the page and right click the `64-Bit (x86) Installer` then copy link address. for `Miniconda`, the installer can be found in the page itself instead of the footer. choose the `Linux 64-bit` installer as well
        - in the VM terminal, enter `wget ANACONDA_DOWNLOAD_LINK` where `ANACONDA_DOWNLOAD_LINK` is the link from the previous step
        - take note of the file name of the installer (the download log will display it)
        - enter `bash FILE_NAME` where `FILE_NAME` is the file name of the downloaded installer (in my case, it is `Anaconda3-2023.03-Linux-x86_64.sh` for `Anaconda`, while `Miniconda3-latest-Linux-x86_64.sh` for `Miniconda`) to start installation
        - follow the steps to finish installation
        - if it asks

                Do you wish the installer to initialize Miniconda3 
                by running conda init? [yes|no]

            choose `yes` so that `conda` is automatically ready to be used even if the VM was just opened
        
        - enter `source ~/.bashrc` to refresh the terminal
        - you should now be able to use `conda`. enter `conda --version` to verify
        - after installation, feel free to delete the installer file using `rm FILE_NAME` (same FILE_NAME from a previous step). then you can enter `ls` afterwards to check if it's deleted
    
    - install `docker`

        - before downloading anything from the native package manager `apt`, enter `sudo apt update; sudo apt upgrade` first to update the packages repository and update outdated packages. this way, we also avoid potential dependency issues when installing packages
        - after updates, enter `sudo apt install docker.io` to download and install `docker`
        - confirm successful `docker` installation by entering `docker --version`
        - try to run a `docker` image

            - enter `docker run hello-world`
            - you will most likely get a `permission denied` error. the fix can be found [here](https://github.com/sindresorhus/guides/blob/main/docker-without-sudo.md). follow the instructions carefully
            - try `docker run hello-world` again, you should be able to successfully run it
    
    - install `docker compose`

        - enter `mkdir bin` to create a `bin` folder in the home directory
        - click the latest release on the right side of the [docker compose github repo](https://github.com/docker/compose)
        - scroll down and look for `docker-compose-linux-x86_64`, right click then copy link address
        - going back to the terminal, enter `cd bin` then `wget DOCKER_COMPOSE_DOWNLOAD_LINK` where `DOCKER_COMPOSE_DOWNLOAD_LINK -O docker-compose` is from the previous step
        - now if we check with `ls`, we can see that `docker-compose` is inside the `bin` folder already
        - if you try to enter `./docker-compose` you will get an error because `docker-compose` is not an executable yet
        - enter `chmod +x docker-compose`
        - try `./docker-compose` again, but this time it should run without errors
        - add `~/bin/docker-compose` to `PATH` so that we can run `docker-compose` from any directory

            - enter `cd` then `nano .bashrc` to edit the bashrc file
            - add `export PATH="${HOME}/bin:${PATH}"` at the end
            - save changes and exit
            - enter `source .bashrc` to refresh the terminal
            - from the home directory, enter `docker-compose`. it should now run as well, confirming successful installation of `docker-compose` and running from any directory
    
    - install `terraform`

        - go to the [official download page](https://developer.hashicorp.com/terraform/downloads) and look for the binary download section. right click then copy link address on the `AMD64` binary
        - from the home directory in the terminal, enter `cd bin` then `wget DOWNLOAD_LINK` where `DOWNLOAD_LINK` is from the previous step
        - since the downloaded file is compressed, we have to unzip it first using `unzip FILE_NAME` where `FILE_NAME` is the file name of the downloaded file. you will get an error because `unzip` is not yet installed
        - `sudo apt install unzip` then try `unzip FILE_NAME` again
        - you should see `terraform` in the directory now if you enter `ls`. verify proper installation with `terraform --version`. if so, feel free to delete the zipped installer using `rm FILE_NAME`. since `~/bin` is already added to `PATH`, `terraform` can now be used from any directory

7. remote SSH into the VM using `VS Code`
    - if you haven't already, install `VS Code` into your PC from this [download link](https://code.visualstudio.com/download) or your native package manager
    - open `VS Code`, click on `Extensions` on the left bar, search and install `Remote - SSH`
    - open the command pallete (at the top bar, click `View`>`Command Palette`)
    - enter `remote ssh` then find and click `Connect to Host`, then choose your SSH `NAME` from earlier
    - a new `VS Code` window should pop up, confirming successful remote SSH