import sys
import os

# Get the path to the 'src' directory
base_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(base_dir, "src")

# Add 'src' to sys.path so we can import modules directly
sys.path.append(src_dir)

from src.core.engine import GameEngine

def main():
    try:
        game = GameEngine()
        game.run()
    except Exception as e:
        print(f"Erro fatal ao iniciar o jogo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
