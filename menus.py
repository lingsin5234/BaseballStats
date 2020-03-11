from menu import Menu, MenuItem
from django.urls import reverse
from . import views as baseball_vw

# add items to the menu
Menu.add_item("main", MenuItem("Home",
                               reverse(baseball_vw.home_page),
                               weight=10))
Menu.add_item("main", MenuItem("Run Jobs",
                               reverse(baseball_vw.run_jobs_view),
                               weight=10))
Menu.add_item("main", MenuItem("View Stats",
                               reverse(baseball_vw.stats_view),
                               weight=10))

