from os import path
import cv2
from PIL import Image

from libs.modules import MTCNNDetectFace, FaceAlignment
from libs.modules.face import Face, Faces
import tests.config as config


class TestFaceAlignment:
    def test_detect_persons_from_sample_image(self):
        configuration = {'model_dir': path.join(config.MODEL_DIR, "mtcnn")}
        detector = MTCNNDetectFace(configuration)
        alignment = FaceAlignment()

        test_image = cv2.imread(path.join(config.TEST_IMAGES, "friends", "friends_01.jpg"))
        image_rgb = cv2.cvtColor(test_image, cv2.COLOR_BGR2RGB)
        image_rgb_PIL = Image.fromarray(image_rgb)
        face_rects, landmarks = detector(image_rgb_PIL)
        faces = Faces([Face(bounding_box=rect, landmarks=land) for rect, land in zip(face_rects, landmarks)])

        for face in faces:
            face.face_align = alignment(image_rgb, face)

        assert all([face.face_align is not None for face in faces])
