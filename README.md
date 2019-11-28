# Image processing pipeline

Modular image processing pipeline using OpenCV and Python generators.  

## Setup environment

This project is using [Conda](https://conda.io) for project environment management.

Setup the project environment:

    $ conda env create -f environment.yml
    $ conda activate pipeline

## Getting started

For detailed description read the article "[Modular image processing pipeline using OpenCV and Python generators](https://medium.com/deepvisionguru/modular-image-processing-pipeline-using-opencv-and-python-generators-9edca3ccb696)" on Medium.
Dont' forget to clap a bit if you like it.

## Resources and Credits

* For Unix like pipeline idea credits goes to this [Gist](https://gist.github.com/alexmacedo/1552724)
* Source of the example images and videos is [pixbay](https://pixabay.com)
* Some ideas and code snippets are borrowed from [pyimagesearch](https://www.pyimagesearch.com/)

## License

[MIT License](LICENSE)

## Idea
1. Create pipeline by merging together several modules, which each one use dict to send the data
2. Make use of computation power of your PC, what able to make your each module:
    2.1 Run in Separate Thread (like I/O operation)
    2.2 Run in New Process (computational expensive )