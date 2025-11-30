from discover import discover_yeelight_bulbs
from methods import BulbController


bulbs = discover_yeelight_bulbs()

if not bulbs:
    print("Nenhuma lâmpada encontrada.")
else:
    print("Encontradas:", bulbs)
    ip, port = bulbs[0]

    controller = BulbController(ip, port, 0)
    controller.turn_on()
    controller.set_ct_abx(3000)
