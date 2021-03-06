import os

from loader.ImageLoader import *
from detector.ObjectDetector import ObjectDetector
from detector.NewObjectDetector import NewObjectDetector
from movements.Pivoting import *
from movements.StringMover import *
from detector.PivotDetector import detect_pivot
from world.World import World
import cv2 as cv
import sys

def create_movie(image_name, frame_width, frame_height):
    # YEAH !!!
    movie_output_path = os.path.join(os.path.dirname(__file__), "MOVIE_OUTPUT")
    try:
        os.mkdir(movie_output_path)
    except:
        pass

    movie_name = os.path.join(movie_output_path, image_name + ".avi")
    vid = cv.VideoWriter(movie_name, -1, 30, (frame_width, frame_height))

    img_path = os.path.join(os.path.dirname(__file__), "world", "render_files")
    file_list = sorted(os.listdir(img_path))

    for f in file_list:
        img = cv.imread(os.path.join(img_path, f))
        vid.write(img)

    cv.destroyAllWindows()
    vid.release()

if __name__ == "__main__":
    img_difficulty = Difficulty.TEST_5_1
    original, new, binary, color_matrix = load_image(img_difficulty)

    detector = NewObjectDetector(new, binary, color_matrix)
    detector.scan_image()

    objects = detector.get_objects()
    detect_pivot(detector)
    # detector.print_label_plane()

    world = World(objects=objects, original_image=original, aggregated_image=new, binary_image=binary,
                  color_matrix=color_matrix, object_detector=detector)

    while world.terminated is not True:
        world.simulate()

    # Make a video
    create_movie(img_difficulty.name, len(original[0]), len(original))


