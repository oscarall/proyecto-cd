setup
  @if [ ! -f .env ]; then cp .env.mock .env; fi

install
	pip install -r requirements.txt;
	