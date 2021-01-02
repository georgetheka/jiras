from jiras import make_jira_etl
from jiras.common.settings import make_settings


def main():
    settings = make_settings()
    etl = make_jira_etl(settings)
    etl.reset()
    etl.extract()
    etl.transform()
    etl.load()


if __name__ == '__main__':
    main()
