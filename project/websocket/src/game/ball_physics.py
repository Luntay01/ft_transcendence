from .models import Vector

class BallPhysics:
    def update_ball_position(self, ball, delta_time):
        """Updates the ball's position based on velocity and time delta."""
        ball.last_position = Vector(x=ball.position.x, y=ball.position.y, z=ball.position.z)
        ball.position.x += ball.velocity.x * delta_time
        ball.position.z += ball.velocity.z * delta_time
        ball.position.y += ball.velocity.y * delta_time
        if ball.position.y < 0:
            ball.position.y = 0  # Prevent ball from going below ground