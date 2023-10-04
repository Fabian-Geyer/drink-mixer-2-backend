from yaml import Loader, load
from coma2.constants import SWAGGER_PATH, SWAGGER_URL
from flask_swagger_ui import get_swaggerui_blueprint

# YAML file path
swagger_yml = load(open(SWAGGER_PATH, 'r'), Loader=Loader)

# register Flask blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, SWAGGER_PATH, config={'spec': swagger_yml})
