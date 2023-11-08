import requests
import pygame
from io import BytesIO
from PIL import Image
from datetime import datetime

pygame.font.init()

FONT1 = pygame.font.SysFont("Arial", 20)

WIDTH, HEIGHT = 1024, 600

WIN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

FPS = 45

API_KEY = "e637479fb23d71b9e9489bd0ea814f9b"
PLAYERNAME = "CuteMid"  # CptnBingo, Foxalete, CuteMid, F-F-B28, Chalro, Zane123_94, TheD3stroy3r376
PLATFORM = "PC"  #  PC, PS4, X1


class Game:

    def __init__(self, survival_time, legend_played):
        self.survival_time = survival_time
        self.legend_played = legend_played
        self.time_game_end = datetime.now()


def get_player():
    url = f"https://api.mozambiquehe.re/bridge?auth={API_KEY}&player={PLAYERNAME}&platform={PLATFORM}"
    response = requests.get(url)
    data = response.json()

    details = {
        "selected_legend": data["realtime"]["selectedLegend"],
        "current_state": data["realtime"]["currentStateAsText"],
        "online": True if data["realtime"]["isOnline"] == 1 else False,
    }

#   Legend ICO image

    response = requests.get(
        data["legends"]["all"][details["selected_legend"]]["ImgAssets"]["icon"])
    if response.status_code == 200:
        pil_ico_img = Image.open(BytesIO(response.content))
        pil_ico_img = pil_ico_img.convert("RGB")
        width, height = pil_ico_img.size[0], pil_ico_img.size[1]
        pil_ico_img = pil_ico_img.crop((109, 0, width - 108, height - 12))
        pil_ico_img_data = pil_ico_img.tobytes()
        width, height = pil_ico_img.width, pil_ico_img.height
        pg_ico_img = pygame.transform.scale(pygame.image.fromstring(pil_ico_img_data, (width, height), "RGB"), (305, 502))
    else:
        pg_ico_img = pygame.transform.scale(pygame.image.load("null.png"), (305, 502))

#   Legend banner image

    response = requests.get(data["legends"]["all"][details["selected_legend"]]["ImgAssets"]["banner"])
    if response.status_code == 200:
        pil_ban_img = Image.open(BytesIO(response.content))
        pil_ban_img = pil_ban_img.convert("RGB")

        width, height = pil_ban_img.size[0], pil_ban_img.size[1]
        pil_ban_img_data = pil_ban_img.tobytes()
        width, height = pil_ban_img.width, pil_ban_img.height
        pg_ban_img = pygame.transform.scale(pygame.image.fromstring(pil_ban_img_data, (width, height), "RGB"), (728, 291))
    else:
        pg_ban_img = pygame.transform.scale(pygame.image.load("null.png"), (728, 291))

    images = {
        "legend_ico": pg_ico_img,
        "legend_banner": pg_ban_img,
    }

    info = {
        "details": details,
        "images": images,
    }

    return info


def display(info, game_history, start_tracker_time):
#   Background colour

    WIN.fill((0, 0, 0))

#   Background images

    WIN.blit(
        info["images"]["legend_banner"],
        pygame.Rect(WIDTH - info["images"]["legend_banner"].get_width(), HEIGHT - info["images"]["legend_banner"].get_height(), info["images"]["legend_banner"].get_width(), info["images"]["legend_banner"].get_height()))

    pygame.draw.rect(
        WIN, (0, 0, 0),
        pygame.Rect(WIDTH - info["images"]["legend_banner"].get_width(), info["images"]["legend_ico"].get_height(), 9, HEIGHT - info["images"]["legend_ico"].get_height()))

    WIN.blit(
        info["images"]["legend_ico"],
        pygame.Rect(0, 0, info["images"]["legend_ico"].get_width(), info["images"]["legend_ico"].get_height()))

#   Player details text

    selected_legend_txt = FONT1.render(
        "Selected legend: {}".format(info["details"]["selected_legend"]), True, (255, 255, 255))
    WIN.blit(selected_legend_txt, (350, 20))

    online_txt = FONT1.render("Online: {}".format(info["details"]["online"]), True, (255, 255, 255))
    WIN.blit(online_txt, (350, 50))

    current_state_txt = FONT1.render("Current state: {}".format(info["details"]["current_state"]), True, (255, 255, 255))
    WIN.blit(current_state_txt, (350, 80))

#   Game history text

    tracker_start_time_txt = FONT1.render(
        "Started tracking at: {}".format(start_tracker_time), True, (255, 255, 255))
    WIN.blit(tracker_start_time_txt, (610, 20))

    game_history_title_txt = FONT1.render("Game history from the last {}/(last 5 games):".format(datetime.now() - start_tracker_time), True, (255, 255, 255))
    WIN.blit(game_history_title_txt, (610, 50))

    y = 80
    for game in game_history:
        game_txt = FONT1.render("Played as {}, Survived for: {}. Game ended {} ago.".format(game.legend_played, game.survival_time, datetime.now - game.time_game_end), True, (255, 255, 255))
        WIN.blit(game_txt, (610, y))

        y += 30

#   UI

    WIN.blit(pygame.image.load("UIbar.png"), pygame.Rect(0, 0, 338, 600))

    pygame.display.update()
    return


def check_game_status(game_history, game_status_last_frame, info):
    if game_status_last_frame == "none":
        return game_history

    if game_status_last_frame[:8] == "In match":
        if info["details"]["current_state"][:8] != "In match":
            game_history.append(Game(game_status_last_frame[10:-1], info["details"]["selected_legend"]))

    return game_history


def main():
    game_history = []
    start_tracker_time = datetime.now()
    game_status_last_frame = "none"

    clock = pygame.time.Clock()
    pygame.display.set_caption("Apex player tracker: {}".format(PLAYERNAME))
    while True:
        clock.tick(FPS)

        info = get_player()
        for game in game_history:
            print("Game {}: {}, {}".format(game_history.index(game), game.legend_played, game.survival_time))
            game_history = check_game_status(game_history, game_status_last_frame, info)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        display(info, game_history, start_tracker_time)

        game_status_last_frame = info["details"]["current_state"]


if __name__ == "__main__":
    main()
