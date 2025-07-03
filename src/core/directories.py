from pathlib import Path


# Define paths
SRC_PATH = Path(__file__).parents[1]
ROOT_PATH = SRC_PATH.parent

RESOURCES_PATH = SRC_PATH.parent / "resources"
QML_PATH = SRC_PATH / "qml"

CONFIGS_PATH = ROOT_PATH / "configs"
THEMES_PATH = SRC_PATH / "themes"
PLUGINS_PATH = SRC_PATH / "plugins"

EXAMPLES_PATH = ROOT_PATH / "examples"


if __name__ == "__main__":
    for path in [SRC_PATH, RESOURCES_PATH, QML_PATH, THEMES_PATH, PLUGINS_PATH]:
        print(path)
