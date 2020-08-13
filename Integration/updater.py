from apscheduler.schedulers.background import BackgroundScheduler

from Integration.inventory_sync import InventorySync


def start():
    bl = InventorySync()
    scheduler = BackgroundScheduler()
    scheduler.add_job(bl.inventorySync, 'interval', minutes=180)
    scheduler.start()