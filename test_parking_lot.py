import unittest
from parking_lot import ParkingLot,ParkingFloor,ParkingService,CarSpot,BikeSpot,TruckSpot,VehicleType

class TestParkingLot(unittest.TestCase):
    def setUp(self):
        self.lot=ParkingLot(1,"City Parking","Warangal")
        self.service=ParkingService(self.lot)
        self.floor=ParkingFloor(1)
        self.service.add_floor(self.floor)
        self.service.add_spot(self.floor,CarSpot("C1"))
        self.service.add_spot(self.floor,CarSpot("C2"))
        self.service.add_spot(self.floor,BikeSpot("B1"))
        self.service.add_spot(self.floor,TruckSpot("T1"))

    def test_add_floor(self):
        floor2=ParkingFloor(2)
        result=self.service.add_floor(floor2)
        self.assertTrue(result)
        self.assertEqual(len(self.lot.floors),2)

    def test_add_spot(self):
        result=self.service.add_spot(self.floor,CarSpot("C3"))
        self.assertTrue(result)
        self.assertEqual(len(self.floor.spots),5)

    def test_park_car(self):
        ticket=self.service.park_vehicle(VehicleType.CAR,"CAR123","Meghana")
        self.assertIsNotNone(ticket)
        self.assertEqual(ticket.status,"ACTIVE")

    def test_park_bike(self):
        ticket=self.service.park_vehicle(VehicleType.BIKE,"BIKE123","Megha")
        self.assertIsNotNone(ticket)
        self.assertEqual(ticket.vehicle.get_vehicle_type(),VehicleType.BIKE)

    def test_duplicate_vehicle(self):
        first=self.service.park_vehicle(VehicleType.CAR,"CAR123","Meghana")
        second=self.service.park_vehicle(VehicleType.CAR,"CAR123","Meghana")
        self.assertIsNotNone(first)
        self.assertIsNone(second)

    def test_no_available_slot(self):
        self.service.park_vehicle(VehicleType.CAR,"CAR001","User1")
        self.service.park_vehicle(VehicleType.CAR,"CAR002","User2")
        third=self.service.park_vehicle(VehicleType.CAR,"CAR003","User3")
        self.assertIsNone(third)

    def test_free_slots(self):
        self.service.park_vehicle(VehicleType.CAR,"CAR123","Meghana")
        free_slots=self.service.get_free_slots(VehicleType.CAR)
        self.assertEqual(len(free_slots),1)

    def test_occupancy(self):
        self.service.park_vehicle(VehicleType.CAR,"CAR123","Meghana")
        occupancy=self.service.get_occupancy()
        self.assertEqual(occupancy["total"],4)
        self.assertEqual(occupancy["occupied"],1)
        self.assertEqual(occupancy["available"],3)

    def test_successful_exit(self):
        ticket=self.service.park_vehicle(VehicleType.CAR,"CAR123","Meghana")
        result=self.service.unpark_vehicle(ticket.ticket_id)
        self.assertTrue(result)
        self.assertEqual(ticket.status,"COMPLETED")

    def test_invalid_ticket(self):
        result=self.service.unpark_vehicle("INVALID999")
        self.assertFalse(result)

    def test_repeated_exit(self):
        ticket=self.service.park_vehicle(VehicleType.CAR,"CAR123","Meghana")
        first_exit=self.service.unpark_vehicle(ticket.ticket_id)
        second_exit=self.service.unpark_vehicle(ticket.ticket_id)
        self.assertTrue(first_exit)
        self.assertFalse(second_exit)

    def test_slot_released_after_exit(self):
        ticket=self.service.park_vehicle(VehicleType.CAR,"CAR123","Meghana")
        self.service.unpark_vehicle(ticket.ticket_id)
        free_slots=self.service.get_free_slots(VehicleType.CAR)
        self.assertEqual(len(free_slots),2)

if __name__=="__main__":
    unittest.main()