import pygame
from .player import Player
from .obstacle import Obstacle

# Game Engine

WHITE = (255, 255, 255)
BROWN = (120, 80, 40)
DARK_GREEN = (30, 100, 30)


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.ground_y = height - 40

        self.player = Player(80, self.ground_y)

        # Task 1: keep the game speed within a fair limit
        self.speed = 6
        self.max_speed = 12
        self.speed_increase_per_frame = 0.003

        self.spawn_interval = 70
        self._spawn_timer = 0
        self.obstacles = []

        self.distance = 0
        self.score = 0
        self.font = pygame.font.SysFont("Arial", 30)
        self.game_over = False

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in (
            pygame.K_SPACE,
            pygame.K_UP,
            pygame.K_w,
        ):
            self.player.jump()

    def handle_input(self):
        # Reserved for continuously-held-key input.
        pass

    def update(self):
        if self.game_over:
            return

        # Task 1: increase speed but never exceed max_speed
        self.speed = min(
            self.speed + self.speed_increase_per_frame,
            self.max_speed,
        )

        self.player.update()

        # Spawn obstacles
        self._spawn_timer += 1

        if self._spawn_timer >= self.spawn_interval:
            self._spawn_timer = 0
            self.obstacles.append(
                Obstacle(self.width, self.ground_y, self.speed)
            )

        # Move obstacles and remember their previous position
        for obstacle in self.obstacles:
            obstacle.previous_x = obstacle.x
            obstacle.move()
            obstacle.speed = self.speed

        # Task 1: improved collision detection
        player_rect = self.player.rect()

        for obstacle in self.obstacles:
            obstacle_rect = obstacle.rect()

            # Normal collision check
            if obstacle_rect.colliderect(player_rect):
                self.game_over = True
                return

            # Swept collision check:
            # detect if the obstacle crossed the player's
            # horizontal area during this frame.
            previous_left = obstacle.previous_x
            previous_right = previous_left + obstacle.width

            current_left = obstacle.x
            current_right = current_left + obstacle.width

            crossed_player = (
                previous_left > player_rect.right
                and current_left <= player_rect.right
            ) or (
                previous_right >= player_rect.left
                and current_right < player_rect.left
            )

            if crossed_player:
                vertical_overlap = (
                    obstacle_rect.bottom > player_rect.top
                    and obstacle_rect.top < player_rect.bottom
                )

                if vertical_overlap:
                    self.game_over = True
                    return

        # Increase score when an obstacle has been passed
        for obstacle in self.obstacles:
            if (
                not obstacle.scored
                and obstacle.x + obstacle.width < self.player.x
            ):
                obstacle.scored = True
                self.score += 1

        # Remove obstacles that have left the screen
        self.obstacles = [
            obstacle
            for obstacle in self.obstacles
            if not obstacle.off_screen()
        ]

        self.distance += self.speed

    def render(self, screen):
        pygame.draw.line(
            screen,
            BROWN,
            (0, self.ground_y),
            (self.width, self.ground_y),
            4,
        )

        pygame.draw.rect(
            screen,
            WHITE,
            self.player.rect(),
        )

        for obstacle in self.obstacles:
            pygame.draw.rect(
                screen,
                DARK_GREEN,
                obstacle.rect(),
            )

        score_text = self.font.render(
            f"Score: {self.score}",
            True,
            (0, 0, 0),
        )

        screen.blit(score_text, (10, 10))

        # Task 2 will replace this with a proper Game Over screen.
        if self.game_over and not getattr(
            self,
            "_game_over_logged",
            False,
        ):
            print(
                "Game over! Final score:",
                self.score,
            )
            self._game_over_logged = True