import random
import tkinter

# GLOBAL CONSTANTS
X_TILES = 10  # The number of tiles in the x direction of the Tetris board
Y_TILES = 20  # The number of tiles in the y direction of the Tetris board
TILE_WIDTH = 33  # The width of each tile in pixels
GHOST_BLOCK_WIDTH = TILE_WIDTH - 2  # The width of a ghost tile in pixels
LEFT_BORDER_WIDTH = 1  # Border width on the left side of the board
RIGHT_BORDER_WIDTH = 12  # The width of the border on the right side of the board
TOP_BORDER_WIDTH = 3  # The height of the border on the top of the board
BOTTOM_BORDER_WIDTH = 1  # The height of the border on the bottom of the board
MIDDLE_GAP = 1  # Width of the gap between the game board and scoreboard/queue
RIGHT_GAP = 1  # Height of the gap between the scoreboard and the queue
SCORE_WIDTH = 10  # The width of the scoreboard in tiles
SCORE_HEIGHT = 2  # The height of the scoreboard in tiles
QUEUE_WIDTH = 10  # The width of the queue in tiles
QUEUE_HEIGHT = Y_TILES - SCORE_HEIGHT - 1  # The height of the queue in tiles
BG_COLOR = "black"  # The background color for the Tetris board, scoreboard, and queue
BORDER_COLOR = "gray"  # The color of the borders around the Tetris board
GRID_COLOR = "gray"  # The color of the grid on the Tetris board.
SCORE_COLOR = "gray"  # The color of the score
GAME_OVER_COLOR = "white"  # The color of the game over message
CENTER = X_TILES / 2 - 1  # The center of the game board
WIDTH = (
    X_TILES + RIGHT_BORDER_WIDTH + LEFT_BORDER_WIDTH
) * TILE_WIDTH  # The width of the window in pixels
HEIGHT = (
    Y_TILES + TOP_BORDER_WIDTH + BOTTOM_BORDER_WIDTH
) * TILE_WIDTH  # The height of the window in pixels
FRAMES_PER_SECOND = 3  # The number of frames and board updates per second
QUEUE_LENGTH = 3  # The length of the queue
GAP_BETWEEN_QUEUE_PIECES = 1  # The gap between shapes in the queue
GHOST_BLOCK_BORDER_WIDTH = 2  # The width of the border of ghost blocks


class Block(object):
    def __init__(self, canvas, x, y, color, ghost_block=False):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.color = color
        if ghost_block is False:
            self.shape = self.canvas.create_rectangle(
                (x + LEFT_BORDER_WIDTH) * TILE_WIDTH,
                (y + TOP_BORDER_WIDTH) * TILE_WIDTH,
                (x + LEFT_BORDER_WIDTH + 1) * TILE_WIDTH,
                (y + TOP_BORDER_WIDTH + 1) * TILE_WIDTH,
                fill=color,
                outline=GRID_COLOR,
            )
        else:
            self.shape = self.canvas.create_rectangle(
                (x + LEFT_BORDER_WIDTH) * TILE_WIDTH + GHOST_BLOCK_BORDER_WIDTH,
                (y + TOP_BORDER_WIDTH) * TILE_WIDTH + GHOST_BLOCK_BORDER_WIDTH,
                (x + LEFT_BORDER_WIDTH + 1) * TILE_WIDTH - 1,
                (y + TOP_BORDER_WIDTH + 1) * TILE_WIDTH - 1,
                fill=BG_COLOR,
                outline=color,
                width=GHOST_BLOCK_BORDER_WIDTH,
            )

    def move(self, dx: int, dy: int) -> None:
        self.x += dx
        self.y += dy
        self.canvas.move(self.shape, dx * TILE_WIDTH, dy * TILE_WIDTH)

    def move_down(self) -> None:
        self.move(0, 1)

    def move_left(self) -> None:
        self.move(-1, 0)

    def move_right(self) -> None:
        self.move(1, 0)

    def delete(self) -> None:
        self.canvas.delete(self.shape)


class StateMachine:
    def __init__(self):
        self.states = [
            "shape_moving",
            "clearing_rows",
            "spawn_shape",
            "paused",
            "game_over",
        ]
        self.state = "spawn_shape"
        self.previous_state = None

    def set_state(self, state: str) -> None:
        if state in self.states:
            self.previous_state = self.state
            self.state = state


class Game(object):
    def __init__(self, main):
        self.main = main
        self.canvas = tkinter.Canvas(main, width=WIDTH, height=HEIGHT, bg=BORDER_COLOR)
        # Create Tetris board
        self.game_area = self.canvas.create_rectangle(
            LEFT_BORDER_WIDTH * TILE_WIDTH,
            TOP_BORDER_WIDTH * TILE_WIDTH,
            LEFT_BORDER_WIDTH * TILE_WIDTH + X_TILES * TILE_WIDTH,
            TOP_BORDER_WIDTH * TILE_WIDTH + Y_TILES * TILE_WIDTH,
            fill=BG_COLOR,
        )
        # Create horizontal lines on Tetris board
        for i in range(1, Y_TILES):
            self.canvas.create_line(
                LEFT_BORDER_WIDTH * TILE_WIDTH,
                TOP_BORDER_WIDTH * TILE_WIDTH + i * TILE_WIDTH,
                LEFT_BORDER_WIDTH * TILE_WIDTH + X_TILES * TILE_WIDTH,
                TOP_BORDER_WIDTH * TILE_WIDTH + i * TILE_WIDTH,
                fill=GRID_COLOR,
            )
        # Create vertical lines on Tetris board
        for i in range(1, X_TILES):
            self.canvas.create_line(
                LEFT_BORDER_WIDTH * TILE_WIDTH + i * TILE_WIDTH,
                TOP_BORDER_WIDTH * TILE_WIDTH,
                LEFT_BORDER_WIDTH * TILE_WIDTH + i * TILE_WIDTH,
                TOP_BORDER_WIDTH * TILE_WIDTH + Y_TILES * TILE_WIDTH,
                fill=GRID_COLOR,
            )
        # Create scoreboard
        self.canvas.create_rectangle(
            (LEFT_BORDER_WIDTH + X_TILES + MIDDLE_GAP) * TILE_WIDTH,
            TOP_BORDER_WIDTH * TILE_WIDTH,
            (LEFT_BORDER_WIDTH + X_TILES + MIDDLE_GAP + SCORE_WIDTH) * TILE_WIDTH,
            (TOP_BORDER_WIDTH + SCORE_HEIGHT) * TILE_WIDTH,
            fill=BG_COLOR,
        )
        # Create queue area
        self.canvas.create_rectangle(
            (LEFT_BORDER_WIDTH + X_TILES + MIDDLE_GAP) * TILE_WIDTH,
            (TOP_BORDER_WIDTH + SCORE_HEIGHT + RIGHT_GAP) * TILE_WIDTH,
            (LEFT_BORDER_WIDTH + X_TILES + MIDDLE_GAP + QUEUE_WIDTH) * TILE_WIDTH,
            (TOP_BORDER_WIDTH + SCORE_HEIGHT + RIGHT_GAP + QUEUE_HEIGHT) * TILE_WIDTH,
            fill=BG_COLOR,
        )

        self.state_machine = StateMachine()

        # Connect keyboard input
        self.canvas.focus_set()
        self.canvas.bind("<Right>", lambda event: self.move_shape_right())
        self.canvas.bind("<Up>", lambda event: self.rotate())
        self.canvas.bind("<Left>", lambda event: self.move_shape_left())
        self.canvas.bind("<Down>", lambda event: self.key_move_shape_down())
        self.canvas.bind("<space>", lambda event: self.key_move_shape_fully_down())
        self.canvas.bind("<d>", lambda event: self.move_shape_right())
        self.canvas.bind("<w>", lambda event: self.rotate())
        self.canvas.bind("<a>", lambda event: self.move_shape_left())
        self.canvas.bind("<s>", lambda event: self.key_move_shape_down())
        self.canvas.bind("<p>", lambda event: self.toggle_pause())
        self.canvas.bind("<r>", lambda event: self.reset())

        # Shapes and their corresponding colors and rotation points
        shape0 = [[1, 0], [0, 1], [1, 1], [2, 1]]
        shape1 = [[2, 0], [0, 1], [1, 1], [2, 1]]
        shape2 = [[0, 0], [0, 1], [1, 1], [2, 1]]
        shape3 = [[0, 0], [0, 1], [0, 2], [0, 3]]
        shape4 = [[0, 0], [0, 1], [1, 1], [1, 2]]
        shape5 = [[0, 0], [0, 1], [1, 0], [1, 1]]
        shape6 = [[1, 0], [1, 1], [0, 1], [0, 2]]
        self.shapes = [shape0, shape1, shape2, shape3, shape4, shape5, shape6]
        rotation_point0 = [CENTER + 1, 1]
        rotation_point1 = [CENTER + 1, 1]
        rotation_point2 = [CENTER + 1, 1]
        rotation_point3 = [CENTER - 0.5, 1.5]
        rotation_point4 = [CENTER + 0, 1]
        rotation_point5 = [CENTER + 0.5, 0.5]
        rotation_point6 = [CENTER + 1, 1]
        self.rotation_points = [
            rotation_point0,
            rotation_point1,
            rotation_point2,
            rotation_point3,
            rotation_point4,
            rotation_point5,
            rotation_point6,
        ]
        self.colors = ["red", "green", "blue", "yellow", "orange", "purple", "cyan"]

        self.shape_queue = [
            random.randint(0, len(self.shapes) - 1) for _ in range(QUEUE_LENGTH)
        ]

        self.shape_queue_blocks = []

        # A list containing the blocks in the active moving shape
        self.active_blocks = []
        self.rotation_point = None

        # The ghost blocks showing where the current active blocks will fall
        self.ghost_blocks = []

        self.inactive_blocks = []

        self.score = 0

        self.score_message = None
        self.game_over_message = None
        self.pause_message = None
        self.draw_score_message()

        # Initiate game loop
        self.canvas.pack()
        self.game_loop()

    def can_move_left(self) -> bool:
        """
        Checks if the moving shape collides with the left wall or an inactive block.
        """
        for b in self.active_blocks:
            if b.x == 0:
                return False
            for i in self.inactive_blocks:
                if b.y == i.y and b.x - 1 == i.x:
                    return False
        return True

    def can_move_right(self) -> bool:
        """
        Check if the shape collides with the right wall or an inactive block.
        """
        for b in self.active_blocks:
            if b.x == X_TILES - 1:
                return False
            for i in self.inactive_blocks:
                if b.y == i.y and b.x + 1 == i.x:
                    return False
        return True

    def can_move_down(self, blocks: list[Block]) -> bool:
        """
        Checks if the shape can move down by checking if it is in the bottom
        row or directly above an inactive block.
        """
        for b in blocks:
            if b.y == Y_TILES - 1:
                return False
            for i in self.inactive_blocks:
                if b.y + 1 == i.y and b.x == i.x:
                    return False
        return True

    def move_shape_down(self) -> None:
        """
        Moves the shape down by one tile if possible.
        """
        if self.can_move_down(self.active_blocks):
            for b in self.active_blocks:
                b.move_down()
            if self.rotation_point:
                self.rotation_point[1] += 1
        else:
            self.deactivate_blocks()

    def key_move_shape_down(self) -> None:
        """
        Moves the shape down by one tile forcefully by keyboard input if possible.
        """
        if self.state_machine.state == "shape_moving":
            self.move_shape_down()
            self.score += 10

    def key_move_shape_fully_down(self) -> None:
        """
        Moves the shape as far down as it can currently go focefully by
        keyboard input.
        """
        if self.state_machine.state == "shape_moving":
            distance = 0
            while self.can_move_down(self.active_blocks):
                self.move_shape_down()
                distance += 1
            self.score += distance * distance * 10
            self.deactivate_blocks()

    def move_shape_right(self) -> None:
        """
        Moves the shape right by one tile if possible.
        """
        if self.state_machine.state == "shape_moving" and self.can_move_right():
            for b in self.active_blocks:
                b.move_right()
            self.rotation_point[0] += 1
            self.update_ghost_blocks()

    def move_shape_left(self) -> None:
        """
        Moves the shape left by one tile if possible.
        """
        if self.state_machine.state == "shape_moving" and self.can_move_left():
            for b in self.active_blocks:
                b.move_left()
            self.rotation_point[0] -= 1
            self.update_ghost_blocks()

    def update_ghost_blocks(self) -> None:
        """
        Draws the ghost blocks at the current shape's current stopping point.
        """
        for b in self.ghost_blocks:
            b.delete()
        self.ghost_blocks = []
        if self.state_machine.state == "shape_moving":
            for b in self.active_blocks:
                ghost_block = Block(self.canvas, b.x, b.y, b.color, ghost_block=True)
                self.ghost_blocks.append(ghost_block)
            while self.can_move_down(self.ghost_blocks):
                for b in self.ghost_blocks:
                    b.move_down()
            # Raise active blocks to the top of the canvas stack so that they appear on top of the ghost blocks
            for b in self.active_blocks:
                self.canvas.tag_raise(b.shape)

    def undo_rotate(self) -> None:
        """
        Undoes a rotation
        """
        for b in self.active_blocks:
            dx = self.rotation_point[0] - b.x
            dy = self.rotation_point[1] - b.y
            b.move(dx - dy, dy + dx)

    def rotate(self) -> None:
        """
        Rotates the active shape by 90 degrees purely mathematically.
        If the rotation causes a collision with inactivate blocks or
        a side wall, it will attempt to move the shape left or right
        by one tile if possible otherwise the rotation will not occur.
        """
        if self.state_machine.state == "shape_moving":
            # Rotate blocks into new position
            for b in self.active_blocks:
                dx = self.rotation_point[0] - b.x
                dy = self.rotation_point[1] - b.y
                b.move(dx + dy, dy - dx)
            # If any of the blocks are colliding with walls in their new position, see if they can be shifted 1 left or right
            for b in self.active_blocks:
                # Check floor for collision, if there is collision undo the rotation since it is invalid:
                if b.y == Y_TILES:
                    self.undo_rotate()
                    return
                # Check left and right walls for collision
                if b.x == -1 and self.can_move_right():
                    self.move_shape_right()
                elif b.x == X_TILES and self.can_move_left():
                    self.move_shape_left()
                # Check inactive blocks for collision
                for i in self.inactive_blocks:
                    if b.x == i.x and b.y == i.y:
                        if self.can_move_left():
                            self.move_shape_left()
                        elif self.can_move_right():
                            self.move_shape_right()
                        # If the shape can't be rotated by shifting it left or right by 1, then it is invalid so undo it
                        else:
                            self.undo_rotate()
                            return
            self.update_ghost_blocks()

    def spawn_shape(self) -> None:
        rng = self.shape_queue.pop(0)
        shape = self.shapes[rng]
        color = self.colors[rng]
        self.rotation_point = list(self.rotation_points[rng])
        for x, y in shape:
            self.active_blocks.append(Block(self.canvas, x + CENTER, y, color))
        self.shape_queue.append(random.randint(0, len(self.shapes) - 1))
        self.draw_shape_queue()

    def draw_shape_queue(self) -> None:
        for b in self.shape_queue_blocks:
            b.delete()
        self.shape_queue_blocks = []
        queue_x = X_TILES + MIDDLE_GAP + QUEUE_WIDTH // 2 - 1
        current_y = SCORE_HEIGHT + RIGHT_GAP + GAP_BETWEEN_QUEUE_PIECES + 1
        for s in self.shape_queue:
            shape = self.shapes[s]
            color = self.colors[s]
            for x, y in shape:
                self.shape_queue_blocks.append(
                    Block(self.canvas, queue_x + x, current_y + y, color)
                )
            current_y += GAP_BETWEEN_QUEUE_PIECES + max([y for _, y in shape]) + 1

    def deactivate_blocks(self) -> None:
        """
        Turns the current active blocks into inactive blocks if they are in collision.
        First we find all blocks that are in collision with the floor or an inactive block,
        keep track of their indices, and add the coordinates above, left, and right of those
        blocks to a queue of coordinates to check. We then process that queue and search for any
        other active blocks above, below, left, or right of any other active blocks we find in
        collision. Finally, we deactivate the blocks that we found to be in collision.

        The algorithm is a bit complex with the current implementation, but it is required in
        order to handle cases where a falling shape is made up of two separate clusters of blocks
        that are not in collision with eachother.
        """
        indices_in_collision = []
        coordinates_to_check = []
        for i in range(len(self.active_blocks)):
            b = self.active_blocks[i]
            x = b.x
            y = b.y
            if y + 1 == Y_TILES or [x, y + 1] in [[b.x, b.y] for b in self.inactive_blocks]:
                indices_in_collision.append(i)
                coordinates_to_check.append([x + 1, y])
                coordinates_to_check.append([x - 1, y])
                coordinates_to_check.append([x, y - 1])
        while len(coordinates_to_check) > 0:
            x, y = coordinates_to_check.pop(0)
            for i in range(len(self.active_blocks)):
                if i not in indices_in_collision:
                    b = self.active_blocks[i]
                    if x == b.x and y == b.y:
                        indices_in_collision.append(i)
                        coordinates_to_check.append([x + 1, y])
                        coordinates_to_check.append([x - 1, y])
                        coordinates_to_check.append([x, y + 1])
                        coordinates_to_check.append([x, y - 1])
                        break
        for i in range(len(self.active_blocks) - 1, -1, -1):
            if i in indices_in_collision:
                self.inactive_blocks.append(self.active_blocks[i])
                del self.active_blocks[i]
        self.state_machine.set_state("clearing_rows")
        self.update_ghost_blocks()

    def delete_blocks(self, blocks) -> None:
        num_blocks = len(blocks)
        for i in range(num_blocks):
            this_block = blocks[num_blocks - 1 - i]
            self.canvas.delete(this_block.shape)
            del blocks[num_blocks - 1 - i]

    def get_filled_rows(self) -> set[int]:
        """
        Returns a set of the row number of filled rows.
        """
        row_to_count = {}
        filled_rows = set()
        for b in self.inactive_blocks:
            if b.y in row_to_count:
                row_to_count[b.y] += 1
                if row_to_count[b.y] == X_TILES:
                    filled_rows.add(b.y)
            else:
                row_to_count[b.y] = 1
        return filled_rows

    def delete_rows(self, rows_to_delete: set[int]) -> None:
        """
        Takes a set of rows and deletes the blocks in those rows.
        Adds blocks above the lowest row deleted to the active blocks
        and gives them the chance to cause more rows to be deleted after
        they fall.
        """
        if len(rows_to_delete) > 0:
            lowest_row_deleted = int(max(rows_to_delete))
            num_inactive_blocks = len(self.inactive_blocks)
            for i in range(num_inactive_blocks):
                this_block = self.inactive_blocks[num_inactive_blocks - 1 - i]
                if this_block.y in rows_to_delete:
                    self.canvas.delete(this_block.shape)
                    del self.inactive_blocks[num_inactive_blocks - 1 - i]
                elif this_block.y < lowest_row_deleted:
                    self.active_blocks.append(this_block)
                    del self.inactive_blocks[num_inactive_blocks - 1 - i]

    def reset(self) -> None:
        """
        Begins a new game after a game over.
        """
        if self.state_machine.state == "game_over":
            self.delete_blocks(self.active_blocks)
            self.delete_blocks(self.inactive_blocks)
            self.canvas.delete(self.game_over_message)
            self.score = 0
            self.state_machine.set_state("spawn_shape")

    def toggle_pause(self) -> None:
        """
        Handles pausing and unpausing.
        """
        if self.state_machine.state == "paused":
            self.state_machine.state = self.state_machine.previous_state
            self.canvas.delete(self.pause_message)
        elif self.state_machine.state != "game_over":
            self.state_machine.set_state("paused")
            self.draw_pause_message()

    def in_collision(self) -> bool:
        """
        Detects whether or not the current active blocks
        are in collision with any inactive blocks.
        """
        for active_block in self.active_blocks:
            for inactive_block in self.inactive_blocks:
                if (
                    active_block.x == inactive_block.x
                    and active_block.y == inactive_block.y
                ):
                    return True
        return False

    def get_score_text(self) -> str:
        """
        Returns a string containing the score.
        """
        return "Score: " + str(self.score)

    def draw_score_message(self) -> None:
        """
        Draws initial score text.
        """
        self.score_message = self.canvas.create_text(
            (LEFT_BORDER_WIDTH + X_TILES + MIDDLE_GAP + SCORE_WIDTH / 2) * TILE_WIDTH,
            (TOP_BORDER_WIDTH + SCORE_HEIGHT / 2) * TILE_WIDTH,
            text=self.get_score_text(),
            fill=SCORE_COLOR,
        )

    def draw_pause_message(self) -> None:
        """
        Draws the pause message when the game is paused.
        """
        self.pause_message = self.canvas.create_text(
            WIDTH / 2,
            HEIGHT / 2,
            text="Paused\nPress P to unpause",
            justify=tkinter.CENTER,
            font=("Segoe UI", "40"),
            fill=GAME_OVER_COLOR,
        )

    def draw_game_over_message(self) -> None:
        """
        Draws the game over message.
        """
        self.game_over_message = self.canvas.create_text(
            WIDTH / 2,
            HEIGHT / 2,
            text=f"Game over! Final score: {self.score}\nPress R to reset",
            justify=tkinter.CENTER,
            font=("Segoe UI", "40"),
            fill=GAME_OVER_COLOR,
        )

    def update_score_text(self) -> None:
        """
        Updates the text in the score message.
        """
        self.canvas.itemconfigure(self.score_message, text=self.get_score_text())

    def game_loop(self):
        if self.state_machine.state == "shape_moving":
            self.move_shape_down()
        elif self.state_machine.state == "clearing_rows":
            if len(self.active_blocks) == 0:
                rows_to_delete = self.get_filled_rows()
                if len(rows_to_delete) > 0:
                    self.delete_rows(rows_to_delete)
                else:
                    self.state_machine.set_state("spawn_shape")
            else:
                self.move_shape_down()
        elif self.state_machine.state == "spawn_shape":
            self.spawn_shape()
            if self.in_collision():
                self.state_machine.set_state("game_over")
                self.draw_game_over_message()
            else:
                self.state_machine.set_state("shape_moving")
                self.update_ghost_blocks()
        self.update_score_text()
        self.main.after(1000 // FRAMES_PER_SECOND, self.game_loop)


def main():
    root = tkinter.Tk()
    Game(root)
    root.mainloop()


if __name__ == "__main__":
    main()
