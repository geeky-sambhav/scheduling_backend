import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app import create_app
from app.config import config_by_name

# Get environment
env = os.environ.get("FLASK_ENV", "development")
config_class = config_by_name.get(env, config_by_name["default"])

# Create application instance
app = create_app(config_class)

if __name__ == "__main__":
    port = int(os.environ.get("PORT"))
    debug = os.environ.get("FLASK_DEBUG")

    app.run(host="0.0.0.0", port=port, debug=debug)
