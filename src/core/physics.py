from typing import Dict

PIPE_CAP_INSET = 1
PIPE_CAP_HEIGHT = 2


class CollisionDetector:
    """Handles collision detection between game entities using AABB (Axis-Aligned Bounding Box)."""

    @staticmethod
    def aabb_collision(box1: Dict, box2: Dict) -> bool:
        """Check if two axis-aligned bounding boxes overlap.

        Args:
            box1: First box with keys x, y, width, height
            box2: Second box with keys x, y, width, height

        Returns:
            True if boxes overlap
        """
        return (
            box1["x"] < box2["x"] + box2["width"]
            and box1["x"] + box1["width"] > box2["x"]
            and box1["y"] < box2["y"] + box2["height"]
            and box1["y"] + box1["height"] > box2["y"]
        )

    @staticmethod
    def check_bird_pipe(bird, pipe) -> bool:
        """
        True if collision detected
        """
        bird_box = bird.get_hitbox()

        if CollisionDetector.aabb_collision(bird_box, pipe.get_top_hitbox()):
            return True

        if CollisionDetector.aabb_collision(bird_box, pipe.get_bottom_hitbox()):
            return True

        top_cap_box = {
            "x": pipe.x + PIPE_CAP_INSET,
            "y": max(0, pipe.y_top - PIPE_CAP_HEIGHT),
            "width": pipe.width - 2 * PIPE_CAP_INSET,
            "height": PIPE_CAP_HEIGHT,
        }
        if CollisionDetector.aabb_collision(bird_box, top_cap_box):
            return True

        bottom_cap_box = {
            "x": pipe.x + PIPE_CAP_INSET,
            "y": pipe.y_bottom,
            "width": pipe.width - 2 * PIPE_CAP_INSET,
            "height": PIPE_CAP_HEIGHT,
        }
        if CollisionDetector.aabb_collision(bird_box, bottom_cap_box):
            return True

        return False

    @staticmethod
    def check_bird_item(bird, item) -> bool:
        """
        True if collision detected
        """
        return CollisionDetector.aabb_collision(bird.get_hitbox(), item.get_hitbox())
