import yaml
from nameko.runners import ServiceRunner
from poker.service import PokerService
from story.service import StoryService


def main():
    with open("config.yaml") as stream:
        config = yaml.safe_load(stream)
        print(config)

    runner = ServiceRunner(config=config)
    runner.add_service(PokerService)
    runner.add_service(StoryService)
    runner.start()


if __name__ == '__main__':
    main()
