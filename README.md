---
section: Guides
chapter: General
title: Visual Mesh Getting Started
description: How to get started with the Visual Mesh.
slug: /guides/general/visualmesh
---

This guide compliments the quickstart guide on the [main Visual Mesh repo](https://github.com/Fastcode/VisualMesh) by being geared towards those with little experience of the [Linux command line (i.e. bash)](https://ubuntu.com/tutorials/command-line-for-beginners#1-overview) or of Machine Learning workflows. If you are already familiar with bash and machine learning, you may prefer to work off the Quickstart guide on the Visual Mesh repo as it is briefer than this guide.

To get started, run this line to check the installation and version of the required programs.

```bash
python3 --version && pip3 --version && git --version && docker --version
```

*this should provide a result similar to that listed below, possibly with higher version numbers, run through the installation guides if this doesn't appear*

```bash
Python 3.8.5
git version 2.25.1
Docker version 20.10.3, build 48d30b5

```

<details>

<Summary>Installing Python3</Summary>

The script to build the dataset is written in Python. The bash terminal simplifies your install massively, so all you need to do is run `sudo apt install python3.8` and it will automatically update to the most recent version of Python 3.8.x

</details>

<details>

<Summary>Installing pip3</Summary>

Pip 3 is a package manager that should be included by default in Python 3.8.x. Be sure to run `sudo apt install python3.8` first to make sure that you've installed it correctly. If for some reason (for example it was removed) pip3 is missing run `sudo apt install python3-pip`.

</details>

<details>

<Summary>Installing Git</Summary>

While you don't strictly need to use git to download the Visual Mesh repo (e.g. you could just download it from github's web interface), git is the recommended way to get and manage the code from the repo. It's recommended to [use GitKraken as a GUI on Linux](https://support.gitkraken.com/how-to-install/), but for the purposes of this tutorial run `sudo apt install git`

</details>

<details>

<Summary>Installing Docker</Summary>

Docker is a program development architecture that we use at NUbots, to install it, run `sudo apt install docker`. If you want to learn more about docker, [check out the documentation](https://docs.docker.com/get-started/overview/) and be sure to ask on Slack if you've got any questions.

</details>

## Clone the Visual Mesh Repo

Use git to clone the Visual mesh repo. When using git on the commandline, git will default to cloning the repo into a folder under your current working directory. Start by navigating to the folder where you want to store the repo: for example, if you wanted to store the visual mesh under `~/code/`, run:

```bash
cd ~
mkdir code
cd code
```

Once you're in the folder you wanted to be in (e.g. `~/code/`), clone the repository with the following command:

```bash
git clone https://github.com/Fastcode/VisualMesh.git
```

## Build the docker image

We specify build steps for docker using a file name `Dockerfile`. This uses similar syntax to a bash script, but is a format specifically used by docker. Navigate to the repository in the terminal (e.g. `cd ~/code/VisualMesh`), then open the dockerfile in a text editor/reader (e.g. `less ./Dockerfile`), and take note of the last two lines: (If you opened the Dockerfile with `less`, navigate with the arrow keys, or vim keys. The command to exit `less` is `q`) Note that you can also run `cat ./Dockerfile` to simply display it inline on your terminal.

```
RUN mkdir /workspace
WORKDIR /workspace
```

These lines tell us that the working directory of the container will be the `/workspace` directory within the container (not the host). Having done a quick check of the dockerfile, we can now tell docker to build the image according to the dockerfile with the following command:

```bash
docker build . --pull -t visualmesh:latest
```

<details>

<Summary>What does this command do?</Summary>
- `docker` is the call to docker
- `build` is the main command being sent to docker
- `.` is telling docker that the build context is the current directory. Docker will look for a file named `Dockerfile` in the build context telling it what to build (so in this case, the current directory).
- `--pull` tells docker to always attempt to pull a newer version of the image
- `-t visualmesh:latest` tells docker that we want to tag the built image as `visualmesh:latest`. We'll see later that when we tell docker to run a container, that we tell docker which image to use by referencing this tag.

</details>

## Make a dummy dataset

For the sake of this guide, we'll use a dummy dataset containing the same image repeated over and over again. *While this will lead to extreme overfitting, it's an easy way to quickly check that the code is running correctly.* Download the example image, mask, and lens file [dummy_data.zip](assets/dummy_data.zip) to your downloads folder.

Now, we're going to make a dummy dataset by repeating these files. We can do this using a bash loop. Assuming that we have the dummy data in `~/Downloads/dummy_data`, and we're going to put the repeated data in `~/Downloads/repeated_data`, run the four commands below:

```bash
cd ~/Downloads

unzip dummy_data.zip

mkdir repeated_data

for i in {1..1000}; do cp ./dummy_data/image.jpg ./repeated_data/image${i}.jpg && cp ./dummy_data/mask.png ./repeated_data/mask${i}.png && cp ./dummy_data/lens.yaml ./repeated_data/lens${i}.yaml; done
```

To ensure that the data was copied sucessfully run the command below which will print all the filenames to the terminal window. Type `clear` afterward to clean up your display.

```bash
ls ~/Downloads/repeated_data
clear
```

### Install the prerequisites to make a tfrecord

We want to convert our dataset from image and text files to the tfrecord format that the visual mesh expects, but to do this we need to install some python libraries to allow python to work with tfrecords. Feel free to use something like conda or virtualenv if you're concerned about ending up with conflicting library versions.

```bash
pip3 install tensorflow tqdm
```

### Make a set of tfrecord

Having made the repeated dataset and installed the libraries required to work with tfrecords, we can now put it into the tfrecord format the visual mesh wants using the `make_dataset.py` script. By default, the visual mesh will look for the dataset inside a folder named `dataset`, so we'll navigate back to the visual mesh repo, make the `dataset` folder, then make the `.tfrecord` files required using the `make_dataset.py` script:

```bash
cd ~/code/VisualMesh
mkdir dataset
./training/make_dataset.py ~/Downloads/repeated_data ./dataset
```

## Configure the training

The visual mesh looks for a `config.yaml` file in the output folder to set the training parameters. An example file `example_net.yaml` can be found in the root of the repo. We'll create an output folder and copy the example parameters into it:

```bash
cd ~/code/VisualMesh
mkdir output
cp example_net.yaml ./output/config.yaml
```

With that, we're almost ready to train the network. To save time, change the configuration to run less training epochs (500 epochs can easily take 30 hours to complete on CPU). Open the config file in a text editor, (e.g. `nano output/config.yaml`) and change the line that says `epochs: 500` to say `epochs: 5`. Also note that the paths for the training, testing and validation tfrecords are set in the config file. *If you have accidentally started training 500 epochs hit `ctrl+c` to keyboard interrupt training, if that doesn't work, open another bash terminal, type `xkill` then click on the training terminal window*

## Train the network

The command to train the network is as below. It's a long command, but it's straightforward if we break it down into the individual parts:

```bash
cd ~/code/VisualMesh
docker run --gpus all -u $(id -u):$(id -g) -it --rm --volume $(pwd):/workspace visualmesh:latest ./mesh.py train output
```

<details>

<Summary>What does this command do?</Summary>
- `docker` is the call to docker
- `run` is the main command being sent to docker
- `--gpus all` tells docker to use the gpus from your system (remove `--gpus all` if you're running on a system without a GPU)
- `-it` tells docker to run in interactive mode with a terminal
- `--rm` tells docker to automatically clean up the temporary files associated with this container
- `--volume $(pwd):/workspace` tells docker to mount the current working directory as `/workspace` inside the container
- `visualmesh:latest` tells docker which image we want to run (note that we built this image and gave it this name in an earlier step)
- `./mesh.py train <path/to/output>` is the command to run inside the container - note that the filesystem inside the container is different to the filesystem outside of the container, but that due to the `--volume` flag, the current working directory is mounted at `/workspace`.

</details>

## Test the network

Testing the network is a very similar command to training, we just replace "train" with "test":

```bash
cd ~/code/VisualMesh
docker run --gpus all -u $(id -u):$(id -g) -it --rm --volume $(pwd):/workspace visualmesh:latest ./mesh.py test output
```

Once the test has finished running, you can inspect the output in `output/test/metrics`.

## Using Tensorboard to inspect the process

[Tensorboard](https://www.tensorflow.org/tensorboard) is a tool that provides a dashboard for visualising of the training process that runs in the browser. For tensorflow, we just pass the output director to tensorboard:

`tensorboard --logdir output`

You should see something like the following:

```
Serving TensorBoard on localhost; to expose to the network, use a proxy or pass --bind_all
TensorBoard 2.4.1 at http://localhost:6006/ (Press CTRL+C to quit)
```

Go to the url specified on your terminal to see the tensorboard dashboard.
