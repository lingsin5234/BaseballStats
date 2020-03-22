from menu import Menu, MenuItem
from django.urls import reverse
from . import views as baseball_vw

# add items to the menu
Menu.add_item("baseball", MenuItem("My Portfolio", url="/", weight=10))
Menu.add_item("baseball", MenuItem("Baseball Project", reverse(baseball_vw.project_markdown), weight=10))
Menu.add_item("baseball", MenuItem("Run Jobs", reverse(baseball_vw.run_jobs_view), weight=10))
Menu.add_item("baseball", MenuItem("View Stats", reverse(baseball_vw.stats_view), weight=10))
