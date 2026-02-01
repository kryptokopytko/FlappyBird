def decide_action(self):
    """Prediction-based decision"""
    bird = self.game.bird
    next_pipe = self._find_next_pipe(pipes, bird.x)

    gap_middle = (next_pipe.y_top + next_pipe.y_bottom) / 2
    risky_target = gap_middle + GAP_OFFSET_BELOW_MIDDLE

    predicted_y = self._predict_position(
        bird.y, bird.velocity, PREDICTION_STEPS=8
    )

    # Jump if predicted position would be too low
    if predicted_y > risky_target + 1:
        return JUMP

    return False
