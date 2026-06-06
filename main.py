from fastapi import FastAPI, Request
import uvicorn

# import jsonresponse
from fastapi.responses import JSONResponse, HTMLResponse

# import Jinja2Templates
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from game import Game2048

templates = Jinja2Templates(directory="./templates/")
app = FastAPI()
app.mount("/static", StaticFiles(directory="./static"), name="static")
game = Game2048()


@app.get("/")
def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "index.html", {"request": request, "docs": str(game)}
    )


@app.get("/board")
def get_board() -> JSONResponse:
    return JSONResponse({"board": game.board.aslist(), "score": int(game.board.score)})


@app.get("/ai_move")
def get_ai_move() -> JSONResponse:
    if game.board.is_game_over:
        game.board.reset()
        return JSONResponse(game.board.aslist(), status_code=400)
    board = game.ai_move()
    return JSONResponse({"board": board.aslist(), "score": int(board.score)})


@app.post("/move/{direction}")
def move(direction):
    if game.board.is_game_over:
        game.board.reset()
        return JSONResponse(game.board.aslist(), status_code=400)
    board = game.move(direction)
    return JSONResponse({"board": board.aslist(), "score": int(board.score)})


@app.post("/reset")
def reset():
    game.board.reset()
    return JSONResponse({"board": game.board.aslist(), "score": int(game.board.score)})


if __name__ == "__main__":
    uvicorn.run(app)
