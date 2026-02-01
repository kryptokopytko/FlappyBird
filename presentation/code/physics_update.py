def update(self, dt: float) -> None:
    """Update bird physics"""
    self.velocity += self.gravity
    self.velocity = min(self.velocity, self.terminal_velocity)
    self.y += self.velocity * dt

def jump(self) -> bool:
    """Execute jump if conditions allow"""
    if self.velocity >= 0:
        self.velocity = self.jump_force
        return True
    return False
