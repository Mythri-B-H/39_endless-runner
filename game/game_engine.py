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

        # -----------------------------------------------
        # Task 1: Speed fairness
        # -----------------------------------------------
        self.speed = 6
        self.max_speed = 12
        self.speed_increase_per_frame = 0.003

        # -----------------------------------------------
        # Task 3: Default difficulty
        # Medium
        # -----------------------------------------------
        self.difficulty = "Medium"
        self.spawn_interval = 70

        self._spawn_timer = 0
        self.obstacles = []

        # Score and distance
        self.distance = 0
        self.score = 0

        # Fonts
        self.font = pygame.font.SysFont(
            "Arial",
            30,
        )

        self.game_over_font = pygame.font.SysFont(
            "Arial",
            60,
            bold=True,
        )

        self.restart_font = pygame.font.SysFont(
            "Arial",
            28,
        )

        self.difficulty_font = pygame.font.SysFont(
            "Arial",
            40,
            bold=True,
        )

        # Game states
        self.game_over = False
        self.selecting_difficulty = False

    # ---------------------------------------------------
    # Keyboard events
    # ---------------------------------------------------
    def handle_event(self, event):

        if event.type != pygame.KEYDOWN:
            return

        # -----------------------------------------------
        # Task 3: Game Over -> Difficulty Selection
        # -----------------------------------------------
        if self.game_over:

            if event.key == pygame.K_RETURN:
                self.selecting_difficulty = True
                return

            if event.key == pygame.K_ESCAPE:
                pygame.event.post(
                    pygame.event.Event(pygame.QUIT)
                )
                return

        # -----------------------------------------------
        # Task 3: Difficulty selection
        # -----------------------------------------------
        if self.selecting_difficulty:

            if event.key == pygame.K_1:
                self.start_new_game(
                    "Easy",
                    5,
                    85,
                )
                return

            if event.key == pygame.K_2:
                self.start_new_game(
                    "Medium",
                    6,
                    70,
                )
                return

            if event.key == pygame.K_3:
                self.start_new_game(
                    "Hard",
                    8,
                    55,
                )
                return

            if event.key == pygame.K_ESCAPE:
                pygame.event.post(
                    pygame.event.Event(pygame.QUIT)
                )
                return

        # -----------------------------------------------
        # Normal gameplay jump
        # -----------------------------------------------
        if not self.game_over and not self.selecting_difficulty:

            if event.key in (
                pygame.K_SPACE,
                pygame.K_UP,
                pygame.K_w,
            ):
                self.player.jump()

    # ---------------------------------------------------
    # Start a new game
    # ---------------------------------------------------
    def start_new_game(
        self,
        difficulty,
        starting_speed,
        spawn_interval,
    ):
        self.difficulty = difficulty

        self.speed = starting_speed
        self.spawn_interval = spawn_interval

        self._spawn_timer = 0
        self.obstacles = []

        self.distance = 0
        self.score = 0

        self.player = Player(
            80,
            self.ground_y,
        )

        self.game_over = False
        self.selecting_difficulty = False

    # ---------------------------------------------------
    # Continuous input
    # ---------------------------------------------------
    def handle_input(self):
        pass

    # ---------------------------------------------------
    # Update game
    # ---------------------------------------------------
    def update(self):

        # Stop gameplay during Game Over
        if self.game_over:
            return

        # Stop gameplay during difficulty selection
        if self.selecting_difficulty:
            return

        # -----------------------------------------------
        # Task 1: Increase speed up to maximum
        # -----------------------------------------------
        self.speed = min(
            self.speed + self.speed_increase_per_frame,
            self.max_speed,
        )

        # Update player
        self.player.update()

        # -----------------------------------------------
        # Spawn obstacles
        # -----------------------------------------------
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

        # -----------------------------------------------
        # Move obstacles
        # -----------------------------------------------
        for obstacle in self.obstacles:

            obstacle.previous_x = obstacle.x

            obstacle.move()

            obstacle.speed = self.speed

        # -----------------------------------------------
        # Collision detection
        # -----------------------------------------------
        player_rect = self.player.rect()

        for obstacle in self.obstacles:

            obstacle_rect = obstacle.rect()

            # Normal collision
            if obstacle_rect.colliderect(
                player_rect
            ):
                self.game_over = True
                return

            # Swept collision
            previous_left = obstacle.previous_x

            previous_right = (
                previous_left
                + obstacle.width
            )

            current_left = obstacle.x

            current_right = (
                current_left
                + obstacle.width
            )

            crossed_player = (
                previous_left > player_rect.right
                and current_left <= player_rect.right
            ) or (
                previous_right >= player_rect.left
                and current_right < player_rect.left
            )

            if crossed_player:

                vertical_overlap = (
                    obstacle_rect.bottom
                    > player_rect.top
                    and obstacle_rect.top
                    < player_rect.bottom
                )

                if vertical_overlap:
                    self.game_over = True
                    return

        # -----------------------------------------------
        # Score
        # -----------------------------------------------
        for obstacle in self.obstacles:

            if (
                not obstacle.scored
                and obstacle.x
                + obstacle.width
                < self.player.x
            ):

                obstacle.scored = True
                self.score += 1

        # -----------------------------------------------
        # Remove off-screen obstacles
        # -----------------------------------------------
        self.obstacles = [
            obstacle
            for obstacle in self.obstacles
            if not obstacle.off_screen()
        ]

        self.distance += self.speed

    # ---------------------------------------------------
    # Render
    # ---------------------------------------------------
    def render(self, screen):

        # -----------------------------------------------
        # Normal game
        # -----------------------------------------------
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

        # Score
        score_text = self.font.render(
            f"Score: {self.score}",
            True,
            (0, 0, 0),
        )

        screen.blit(
            score_text,
            (10, 10),
        )

        # -----------------------------------------------
        # Task 2: Game Over
        # -----------------------------------------------
        if self.game_over:

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

        # -----------------------------------------------
        # Task 3: Difficulty selection
        # -----------------------------------------------
        if self.selecting_difficulty:

            overlay = pygame.Surface(
                (self.width, self.height),
                pygame.SRCALPHA,
            )

            overlay.fill(
                (0, 0, 0, 200)
            )

            screen.blit(
                overlay,
                (0, 0),
            )

            title = (
                self.difficulty_font.render(
                    "SELECT DIFFICULTY",
                    True,
                    WHITE,
                )
            )

            title_rect = title.get_rect(
                center=(
                    self.width // 2,
                    120,
                )
            )

            screen.blit(
                title,
                title_rect,
            )

            easy = self.restart_font.render(
                "1 - EASY",
                True,
                WHITE,
            )

            medium = self.restart_font.render(
                "2 - MEDIUM",
                True,
                WHITE,
            )

            hard = self.restart_font.render(
                "3 - HARD",
                True,
                WHITE,
            )

            exit_text = self.restart_font.render(
                "ESC - EXIT",
                True,
                WHITE,
            )

            screen.blit(
                easy,
                easy.get_rect(
                    center=(
                        self.width // 2,
                        220,
                    )
                ),
            )

            screen.blit(
                medium,
                medium.get_rect(
                    center=(
                        self.width // 2,
                        270,
                    )
                ),
            )

            screen.blit(
                hard,
                hard.get_rect(
                    center=(
                        self.width // 2,
                        320,
                    )
                ),
            )

            screen.blit(
                exit_text,
                exit_text.get_rect(
                    center=(
                        self.width // 2,
                        390,
                    )
                ),
            )