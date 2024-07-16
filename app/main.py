import logging
import os
from app.app_page_controller import AppPageController
from app.config.create_database import DatabaseInitializer

# Create a log file is not exists
log_dir = "logs"
log_file = os.path.join(log_dir, "log.log")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

logging.warning("=== Starting the application")



def main():
    try:
        app_page_controller = AppPageController()
        app_page_controller.mainloop()
        DatabaseInitializer.init_db()
    
    except Exception as e:
        logging.error(f"Main () === error occured: {e}")


if __name__ == "__main__":
    main()
