import os

from pipeline.load_images import LoadImages
from pipeline.cascade_detect_faces import CascadeDetectFaces
from pipeline.save_faces import SaveFaces
from pipeline.save_summary import SaveSummary
from pipeline.display_summary import DisplaySummary
from pipeline.pipeline_manager_v2 import Task


def parse_args():
    import argparse

    # Parse command line arguments
    ap = argparse.ArgumentParser(description="Image processing pipeline")
    ap.add_argument("-i", "--input", required=True,
                    help="path to input image files")
    ap.add_argument("-o", "--output", default="output",
                    help="path to output directory")
    ap.add_argument("-os", "--out-summary", default=None,
                    help="output JSON summary file name")
    ap.add_argument("-c", "--classifier", default="models/haarcascade/haarcascade_frontalface_default.xml",
                    help="path to where the face cascade resides")

    return ap.parse_args()


def main(args):
    # Create pipeline steps
    load_images = LoadImages(args.input)

    detect_faces = CascadeDetectFaces(args.classifier)

    save_faces = SaveFaces(args.output)

    if args.out_summary:
        summary_file = os.path.join(args.output, args.out_summary)
        save_summary = SaveSummary(summary_file)

    display_summary = DisplaySummary()

    # Create image processing pipeline
    pipeline = Task(load_images) | Task(detect_faces, 8) | Task(save_faces)
    if args.out_summary:
        pipeline |= Task(save_summary)
    pipeline |= Task(display_summary)

    # Iterate through pipeline
    for a in pipeline:
        pass


if __name__ == "__main__":
    args = parse_args()
    main(args)
