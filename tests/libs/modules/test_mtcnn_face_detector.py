from os import path
import cv2
from PIL import Image

from libs.modules import MTCNNDetectFace
from libs.modules.face import Face, Faces
import tests.config as config


class TestMTCNNFaceDetector:
    def test_detect_persons_from_sample_image(self):
        configuration = {'model_dir': path.join(config.MODEL_DIR, "mtcnn")}
        detector = MTCNNDetectFace(configuration)

        test_image = cv2.imread(path.join(config.TEST_IMAGES, "friends", "friends_01.jpg"))
        image_rgb = cv2.cvtColor(test_image, cv2.COLOR_BGR2RGB)
        image_rgb = Image.fromarray(image_rgb)
        face_rects, landmarks = detector(image_rgb)
        faces = Faces([Face(bounding_box=rect, landmarks=land) for rect, land in zip(face_rects, landmarks)])
        assert len(faces) == 3
