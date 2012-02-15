# -*- coding: utf-8 -*-
{
        "name"    : "chricar_stocklocation_moves",
	"version" : "0.1",
	"author"  : "ChriCar Beteiligungs- und Beratungs- GmbH",
	"category": "Warehouse Management",
	"depends" : ["base","stock","c2c_stock_accounting"],
        "init_xml": [],
	"update_xml": ["stocklocation_move.xml","security/ir.model.access.csv"],
	"active"  : False,
	"installable": True,
	"description": """Analysis of moves per location
	(Group by Category is broken - related field)
        """
}
