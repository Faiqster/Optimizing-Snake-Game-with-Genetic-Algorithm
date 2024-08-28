import pygame, sys,time, random, numpy as np

# Difficulty settings
difficulty = 100

# Window size
frame_size_x = 720
frame_size_y = 480

# Initialize Pygame
check_errors = pygame.init()
if check_errors[1] > 0:
    print(f'[!] Had {check_errors[1]} errors when initialising game, exiting...')
    sys.exit(-1)
else:
    print('[+] Game successfully initialised')

# Initialize game window
pygame.display.set_caption('SnakeAI')
game_window = pygame.display.set_mode((frame_size_x, frame_size_y))

# Colors (R, G, B)
black = pygame.Color(0, 0, 0)
white = pygame.Color(255, 255, 255)
red = pygame.Color(255, 0, 0)
green = pygame.Color(0, 255, 0)
blue = pygame.Color(0, 0, 255)

# FPS (frames per second) controller
fps_controller = pygame.time.Clock()

# Snake class
class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        self.pos = [100, 50]
        self.body = [[100, 50], [90, 50], [80, 50]]
        self.direction = 'RIGHT'
        self.change_to = self.direction
        self.food_pos = [random.randrange(1, (frame_size_x // 10)) * 10, random.randrange(1, (frame_size_y // 10)) * 10]
        self.food_spawn = True
        self.score = 0

    def change_dir(self, change_to):
        if change_to == 'UP' and self.direction != 'DOWN':
            self.direction = 'UP'
        if change_to == 'DOWN' and self.direction != 'UP':
            self.direction = 'DOWN'
        if change_to == 'LEFT' and self.direction != 'RIGHT':
            self.direction = 'LEFT'
        if change_to == 'RIGHT' and self.direction != 'LEFT':
            self.direction = 'RIGHT'

    def move(self):
        if self.direction == 'UP':
            self.pos[1] -= 10
        if self.direction == 'DOWN':
            self.pos[1] += 10
        if self.direction == 'LEFT':
            self.pos[0] -= 10
        if self.direction == 'RIGHT':
            self.pos[0] += 10

    def grow(self):
        self.body.insert(0, list(self.pos))
        if self.pos[0] == self.food_pos[0] and self.pos[1] == self.food_pos[1]:
            self.score += 1
            self.food_spawn = False
        else:
            self.body.pop()

        if not self.food_spawn:
            self.food_pos = [random.randrange(1, (frame_size_x // 10)) * 10, random.randrange(1, (frame_size_y // 10)) * 10]
        self.food_spawn = True

    def check_collision(self):
        if self.pos[0] < 0 or self.pos[0] > frame_size_x - 10 or self.pos[1] < 0 or self.pos[1] > frame_size_y - 10:
            return True
        for block in self.body[1:]:
            if self.pos[0] == block[0] and self.pos[1] == block[1]:
                return True
        return False

    def get_state(self):
        return {
            "position": self.pos,
            "body": self.body,
            "direction": self.direction,
            "food": self.food_pos,
            "score": self.score
        }

    def set_state(self, state):
        self.pos = state["position"]
        self.body = state["body"]
        self.direction = state["direction"]
        self.food_pos = state["food"]
        self.score = state["score"]

# Genetic Algorithm Functions
def create_population(size):
    return [Snake() for _ in range(size)]

def fitness(snake):
    # Reward for survival time
    survival_reward = snake.score * 0.1  # Reward per step survived
    
    # Penalize collisions
    collision_penalty = -10 if snake.check_collision() else 0  # Penalize collisions
    
    # Reward proximity to food
    food_distance = np.sqrt((snake.pos[0] - snake.food_pos[0])**2 + (snake.pos[1] - snake.food_pos[1])**2)
    food_reward = 1.0 / (food_distance + 1)  # Reward inversely proportional to distance to food
    
    # Reward snake length
    length_reward = len(snake.body) * 0.1  # Reward per body length
    
    # Combine rewards and penalties
    total_fitness = survival_reward + collision_penalty + food_reward + length_reward
    
    # Ensure non-negative fitness
    total_fitness = max(total_fitness, 0)
    
    return total_fitness


def selection(population):
    fitnesses = np.array([fitness(snake) for snake in population])
    total_fitness = np.sum(fitnesses)
    
    # Handle the case where all fitness values are zero
    if total_fitness == 0:
        probabilities = np.ones(len(fitnesses)) / len(fitnesses)
    else:
        probabilities = fitnesses / total_fitness
    
    # Ensure no NaN or negative values in probabilities
    probabilities = np.nan_to_num(probabilities, nan=0.0, posinf=0.0, neginf=0.0)
    probabilities = np.clip(probabilities, 0, 1)
    
    selected_indices = np.random.choice(len(population), size=2, p=probabilities)
    selected_snakes = [population[i] for i in selected_indices]
    return selected_snakes


def crossover(parent1, parent2):
    child = Snake()
    child.set_state(parent1.get_state() if random.random() < 0.5 else parent2.get_state())
    return child

def mutate(snake):
    if random.random() < mutation_rate:
        snake.direction = random.choice(['UP', 'DOWN', 'LEFT', 'RIGHT'])
    return snake

def genetic_algorithm(population):
    new_population = []
    for _ in range(len(population)):
        parent1, parent2 = selection(population)
        child = crossover(parent1, parent2)
        child = mutate(child)
        new_population.append(child)
    return new_population

# Heuristic for snake movement
def heuristic(snake):
    # Move towards the food
    if snake.pos[0] < snake.food_pos[0]:
        snake.change_dir('RIGHT')
    elif snake.pos[0] > snake.food_pos[0]:
        snake.change_dir('LEFT')
    elif snake.pos[1] < snake.food_pos[1]:
        snake.change_dir('DOWN')
    elif snake.pos[1] > snake.food_pos[1]:
        snake.change_dir('UP')

# Main logic
generation = 0
population_size = 2
mutation_rate = 0.01
generations = 1000

population = create_population(population_size)
def show_score(choice, color, font, size, score, generation):
    score_font = pygame.font.SysFont(font, size)
    score_surface = score_font.render('Score : ' + str(score), True, color)
    generation_surface = score_font.render('Generation : ' + str(generation), True, color)
    score_rect = score_surface.get_rect()
    generation_rect = generation_surface.get_rect()
    if choice == 1:
        score_rect.midtop = (frame_size_x / 10, 15)
        generation_rect.midtop = (frame_size_x / 1.17, 15)
    else:
        score_rect.midtop = (frame_size_x / 2, frame_size_y / 1.25)
        generation_rect.midtop = (frame_size_x / 2, frame_size_y / 1.35)
    game_window.blit(score_surface, score_rect)
    game_window.blit(generation_surface, generation_rect)

while True:
    generation += 1
    for snake in population:
        snake.reset()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # Game logic
            heuristic(snake)  # Use heuristic for initial movement
            snake.move()
            snake.grow()
            if snake.check_collision():
                break

            # GFX
            game_window.fill(black)
            for pos in snake.body:
                pygame.draw.rect(game_window, green, pygame.Rect(pos[0], pos[1], 10, 10))
            pygame.draw.rect(game_window, white, pygame.Rect(snake.food_pos[0], snake.food_pos[1], 10, 10))
            show_score(1, white, 'consolas', 20, snake.score, generation)

            pygame.display.update()
            fps_controller.tick(difficulty)

    # Genetic Algorithm
    population = genetic_algorithm(population)

    # Display generation info
    print(f'Generation: {generation}')

    if generation >= generations:
        break

