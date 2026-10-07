import pygame
from .player import Player
from .obstacle import Obstacle


# Colors
WHITE = (255, 255, 255)
BROWN = (120, 80, 40)
DARK_GREEN = (30, 100, 30)


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.ground_y = height - 40

        # Player
        self.player = Player(80, self.ground_y)

        # --------------------------------------------------
        # Task 1: Speed fairness
        # --------------------------------------------------
        self.speed = 6
        self.max_speed = 12
        self.speed_increase_per_frame = 0.003

        # Obstacle settings
        self.spawn_interval = 70
        self._spawn_timer = 0
        self.obstacles = []

        # Score and distance
        self.distance = 0
        self.score = 0

        # Fonts
        self.font = pygame.font.SysFont("Arial", 30)
        self.game_over_font = pygame.font.SysFont(
            "Arial",
            60,
            bold=True,
        )
        self.restart_font = pygame.font.SysFont(
            "Arial",
            28,
        )

        # Game state
        self.game_over = False

    # ------------------------------------------------------
    # Handle keyboard events
    # ------------------------------------------------------
    def handle_event(self, event):
        if (
            event.type == pygame.KEYDOWN
            and event.key
            in (
                pygame.K_SPACE,
                pygame.K_UP,
                pygame.K_w,
            )
        ):
            self.player.jump()

    # ------------------------------------------------------
    # Handle continuous input
    # ------------------------------------------------------
    def handle_input(self):
        # Reserved for continuously-held-key input.
        # Jumping is handled in handle_event().
        pass

    # ------------------------------------------------------
    # Update game
    # ------------------------------------------------------
    def update(self):
        # Stop updating after Game Over
        if self.game_over:
            return

        # --------------------------------------------------
        # Task 1: Increase speed but keep a maximum limit
        # --------------------------------------------------
        self.speed = min(
            self.speed + self.speed_increase_per_frame,
            self.max_speed,
        )

        # Update player physics
        self.player.update()

        # --------------------------------------------------
        # Spawn obstacles
        # --------------------------------------------------
        self._spawn_timer += 1

        if self._spawn_timer >= self.spawn_interval:
            self._spawn_timer = 0

            self.obstacles.append(
                Obstacle(
                    self.width,
                    self.ground_y,
                    self.speed,
                )
            )

        # --------------------------------------------------
        # Move obstacles
        # --------------------------------------------------
        for obstacle in self.obstacles:
            # Remember obstacle position BEFORE movement
            obstacle.previous_x = obstacle.x

            # Move obstacle
            obstacle.move()

            # Keep obstacle speed synchronized
            obstacle.speed = self.speed

        # --------------------------------------------------
        # Task 1: Collision detection
        # --------------------------------------------------
        player_rect = self.player.rect()

        for obstacle in self.obstacles:

            obstacle_rect = obstacle.rect()

            # Normal collision check
            if obstacle_rect.colliderect(player_rect):
                self.game_over = True
                return

            # --------------------------------------------------
            # Swept collision check
            #
            # This checks whether the obstacle crossed the
            # player's position between two frames.
            # --------------------------------------------------

            previous_left = obstacle.previous_x
            previous_right = (
                previous_left + obstacle.width
            )

            current_left = obstacle.x
            current_right = (
                current_left + obstacle.width
            )

            crossed_player = (
                previous_left > player_rect.right
                and current_left <= player_rect.right
            ) or (
                previous_right >= player_rect.left
                and current_right < player_rect.left
            )

            if crossed_player:

                # Check vertical overlap
                vertical_overlap = (
                    obstacle_rect.bottom
                    > player_rect.top
                    and obstacle_rect.top
                    < player_rect.bottom
                )

                if vertical_overlap:
                    self.game_over = True
                    return

        # --------------------------------------------------
        # Increase score when obstacle is passed
        # --------------------------------------------------
        for obstacle in self.obstacles:

            if (
                not obstacle.scored
                and obstacle.x + obstacle.width
                < self.player.x
            ):
                obstacle.scored = True
                self.score += 1

        # --------------------------------------------------
        # Remove obstacles that left the screen
        # --------------------------------------------------
        self.obstacles = [
            obstacle
            for obstacle in self.obstacles
            if not obstacle.off_screen()
        ]

        # Increase distance
        self.distance += self.speed

    # ------------------------------------------------------
    # Render game
    # ------------------------------------------------------
    def render(self, screen):

        # --------------------------------------------------
        # Ground
        # --------------------------------------------------
        pygame.draw.line(
            screen,
            BROWN,
            (0, self.ground_y),
            (self.width, self.ground_y),
            4,
        )

        # --------------------------------------------------
        # Player
        # --------------------------------------------------
        pygame.draw.rect(
            screen,
            WHITE,
            self.player.rect(),
        )

        # --------------------------------------------------
        # Obstacles
        # --------------------------------------------------
        for obstacle in self.obstacles:

            pygame.draw.rect(
                screen,
                DARK_GREEN,
                obstacle.rect(),
            )

        # --------------------------------------------------
        # Score
        # --------------------------------------------------
        score_text = self.font.render(
            f"Score: {self.score}",
            True,
            (0, 0, 0),
        )

        screen.blit(
            score_text,
            (10, 10),
        )

        # --------------------------------------------------
        # Task 2: Game Over screen
        # --------------------------------------------------
        if self.game_over:

            # Dark transparent overlay
            overlay = pygame.Surface(
                (self.width, self.height),
                pygame.SRCALPHA,
            )

            overlay.fill(
                (0, 0, 0, 160)
            )

            screen.blit(
                overlay,
                (0, 0),
            )

            # --------------------------------------------------
            # GAME OVER text
            # --------------------------------------------------
            game_over_text = (
                self.game_over_font.render(
                    "GAME OVER",
                    True,
                    WHITE,
                )
            )

            game_over_rect = (
                game_over_text.get_rect(
                    center=(
                        self.width // 2,
                        self.height // 2 - 60,
                    )
                )
            )

            screen.blit(
                game_over_text,
                game_over_rect,
            )

            # --------------------------------------------------
            # Final score
            # --------------------------------------------------
            final_score_text = (
                self.restart_font.render(
                    f"Final Score: {self.score}",
                    True,
                    WHITE,
                )
            )

            final_score_rect = (
                final_score_text.get_rect(
                    center=(
                        self.width // 2,
                        self.height // 2,
                    )
                )
            )

            screen.blit(
                final_score_text,
                final_score_rect,
            )

            # --------------------------------------------------
            # Replay instruction
            # --------------------------------------------------
            restart_text = (
                self.restart_font.render(
                    "Press ENTER to continue",
                    True,
                    WHITE,
                )
            )

            restart_rect = (
                restart_text.get_rect(
                    center=(
                        self.width // 2,
                        self.height // 2 + 50,
                    )
                )
            )

            screen.blit(
                restart_text,
                restart_rect,
            )