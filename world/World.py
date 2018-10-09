from world.Reasoner import Reasoner
from movements.Movements import *
from objects.Colors import Colors

from detector.NewObjectDetector import *

from movements.Falling import *
from movements.Pivoting import *

import cv2 as cv

import os
import numpy as np


class World:
    def __init__(self, objects, original_image, aggregated_image, binary_image, color_matrix, object_detector):
        self.terminated = False
        self.steps = 0

        self.world_row = len(original_image)
        self.world_col = len(original_image[0])

        self.objects = objects
        self.original_image = original_image
        self.aggregated_image = aggregated_image
        self.binary_image = binary_image
        self.color_matrix = color_matrix

        self.object_detector = object_detector

        self.reasoner = Reasoner()

    def simulate(self):
        """
        Starts the simulation
        :return: Terminated: Bool
        """

        # Classify all objects that has to fall. "check stability"
        # Given the objects that are going to fall, render them "move_object_down"
        # Continue

        unstable = self.simulate_falling()
        reconstructed_image = self.reconstruct_image(self.objects)

        neighbors = self.detect_contact(unstable)
        self.contact_interaction(neighbors)

        self.update_render(self.steps, reconstructed_image)

        self.reload_image(step=self.steps)

        print("Step : ", self.steps)
        self.steps += 1
        if len(unstable) == 0:
            self.terminated = True

    def simulate_falling(self):
        unstable_objects, unstable_centeroids = self.reasoner.check_stability_of_all_objects(self.object_detector,
                                                                                             self.objects)
        print("Unstable Objects: ", unstable_objects)
        print("Unstable Centeroids: ", unstable_centeroids)

        self.move_unstable_objects_down(unstable_objects)
        return unstable_objects

    def move_unstable_objects_down(self, unstable_objects):
        for unstable_id in unstable_objects:
            move_object_down(self.objects[unstable_id])

    def detect_contact(self, unstable):
        neighbors = {}
        for obj_id in unstable:
            neighbor = get_neighbors(self.object_detector, obj_id)
            if len(neighbor) > 1:
                neighbors[obj_id] = neighbor[1:]

        print(neighbors)
        return neighbors

    def contact_interaction(self, neighbors):
        for key in neighbors.keys():
            # new_image, new_coord, new_center = rotate_pivot(self.object_detector, self.aggregated_image, neighbors[key][0], key, 'counterclockwise')
            new_image, new_coord, new_center = rotate_pivot(self.object_detector, self.aggregated_image,
                                                            2, 3, 'counterclockwise')
            self.objects[neighbors[key][0]].coordinates = new_coord

    def reload_image(self, step):
        # reload previous image
        dir_path = os.path.join(os.path.dirname(__file__), "render_files")
        path = os.path.join(dir_path, str(step).zfill(5) + ".png")
        self.original_image, self.aggregated_image, self.binary_image, self.color_matrix = reload(path)

        det = NewObjectDetector(self.original_image, self.binary_image, self.color_matrix)
        det.scan_image()

        self.objects = det.get_objects()

    def get_color_BGR(self, color_string):
        if color_string == "w":
            return Colors.W.value

        if color_string == "d":
            return Colors.D.value

        if color_string == "b":
            return Colors.B.value

        if color_string == "y":
            return Colors.Y.value

        if color_string == "g":
            return Colors.G.value

    def update_render(self, step, reconstructed_image):
        """
        Updates state after an iteration
        :return:
        """
        dir_path = os.path.join(os.path.dirname(__file__), "render_files")
        try:
            os.mkdir(dir_path)
        except:
            pass

        path = os.path.join(dir_path, str(step).zfill(5) + ".png")
        cv.imwrite(path, reconstructed_image)

    def reconstruct_image(self, objects):
        reconstructed_image = np.full(shape=(self.world_row, self.world_col, 3), fill_value=self.get_color_BGR(color_string="w"))

        for object_idx in range(1, len(objects) + 1):
            coordinates = objects[object_idx].get_coordinates()
            color = objects[object_idx].get_color()

            for coord in coordinates:
                # Push color
                reconstructed_image[coord[0]][coord[1]] = self.get_color_BGR(color)

        return reconstructed_image

    def reconstruct_single_object(self, obj):
        reconstructed_image = np.full(shape=(self.world_row, self.world_col, 3), fill_value=self.get_color_BGR(color_string="w"))

        coordinates = obj.get_coordinates()
        color = obj.get_color()

        for coord in coordinates:
            # Push color
            try:
                reconstructed_image[coord[0]][coord[1]] = self.get_color_BGR(color)
            except:
                pass

        return reconstructed_image

