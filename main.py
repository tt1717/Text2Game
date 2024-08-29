import sys
import importlib

if __name__ == '__main__':
    # コマンドライン引数からゲーム名を取得
    if len(sys.argv) != 2:
        print("Usage: python main.py <game_name>")
        sys.exit(1)

    game_name = sys.argv[1]

    try:
        # 動的にモジュールをインポート
        game_module = importlib.import_module(f"game.{game_name}")
        
        # GameUIクラスを取得
        GameUI = getattr(game_module, 'GameUI')

        # GameUIインスタンスを作成して実行
        f = GameUI()
        f.pack()
        f.mainloop()
    except ModuleNotFoundError:
        print(f"Error: The specified game '{game_name}' was not found.")
    except AttributeError:
        print(f"Error: The specified game '{game_name}' does not have a 'GameUI' class.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
