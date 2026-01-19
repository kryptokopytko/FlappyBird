"""Physics and collision detection system."""


class CollisionDetector:
    """Handles collision detection between entities."""

    @staticmethod
    def aabb_collision(box1, box2):
        """
        Axis-Aligned Bounding Box collision detection.

        Args:
            box1: Dict with 'x', 'y', 'width', 'height'
            box2: Dict with 'x', 'y', 'width', 'height'

        Returns:
            True if boxes collide, False otherwise
        """
        return (
            box1['x'] < box2['x'] + box2['width'] and
            box1['x'] + box1['width'] > box2['x'] and
            box1['y'] < box2['y'] + box2['height'] and
            box1['y'] + box1['height'] > box2['y']
        )

    @staticmethod
    def check_bird_pipe(bird, pipe):
        """
        Check if bird collides with a pipe.

        Args:
            bird: Bird entity
            pipe: Pipe entity

        Returns:
            True if collision detected, False otherwise
        """
        bird_box = bird.get_hitbox()

        # Check collision with top pipe
        top_pipe_box = pipe.get_top_hitbox()
        if CollisionDetector.aabb_collision(bird_box, top_pipe_box):
            return True

        # Check collision with bottom pipe
        bottom_pipe_box = pipe.get_bottom_hitbox()
        if CollisionDetector.aabb_collision(bird_box, bottom_pipe_box):
            return True

        # Check collision with top pipe decorative cap (last 2 lines of top pipe)
        top_cap_box = {
            'x': pipe.x + 1,
            'y': max(0, pipe.y_top - 2),  # Allow y=0 for ceiling caps
            'width': pipe.width - 2,
            'height': 2
        }
        if CollisionDetector.aabb_collision(bird_box, top_cap_box):
            return True

        # Check collision with bottom pipe decorative cap (first 2 lines of bottom pipe)
        bottom_cap_box = {
            'x': pipe.x + 1,
            'y': pipe.y_bottom,
            'width': pipe.width - 2,
            'height': 2
        }
        if CollisionDetector.aabb_collision(bird_box, bottom_cap_box):
            return True

        return False

    @staticmethod
    def check_bird_item(bird, item):
        """
        Check if bird collides with an item (coin, powerup, etc.).

        Args:
            bird: Bird entity
            item: Item entity

        Returns:
            True if collision detected, False otherwise
        """
        bird_box = bird.get_hitbox()
        item_box = item.get_hitbox()
        return CollisionDetector.aabb_collision(bird_box, item_box)
