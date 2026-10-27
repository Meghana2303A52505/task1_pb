from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime

class VehicleType(Enum):
    CAR="CAR"
    BIKE="BIKE"
    TRUCK="TRUCK"

class User:
    def __init__(self,user_id,name,phone):
        self.user_id=user_id
        self.name=name
        self.phone=phone
        self.tickets=[]

    def reserve_spot(self,parking_lot):
        return parking_lot.reserve_spot()

class Admin:
    def __init__(self,admin_id,name):
        self.admin_id=admin_id
        self.name=name

    def add_floor(self,parking_lot,floor):
        return parking_lot.add_floor(floor)

    def add_spot(self,floor,spot):
        return floor.add_spot(spot)

    def get_occupancy(self,parking_lot):
        return parking_lot.get_occupancy()

class Vehicle(ABC):
    def __init__(self,vehicle_number,owner_name):
        self.vehicle_number=vehicle_number
        self.owner_name=owner_name

    @abstractmethod
    def get_vehicle_type(self):
        pass

class Car(Vehicle):
    def get_vehicle_type(self):
        return VehicleType.CAR

class Bike(Vehicle):
    def get_vehicle_type(self):
        return VehicleType.BIKE

class Truck(Vehicle):
    def get_vehicle_type(self):
        return VehicleType.TRUCK

class VehicleFactory:
    @staticmethod
    def create_vehicle(vehicle_type,vehicle_number,owner_name):
        if vehicle_type==VehicleType.CAR:
            return Car(vehicle_number,owner_name)
        if vehicle_type==VehicleType.BIKE:
            return Bike(vehicle_number,owner_name)
        if vehicle_type==VehicleType.TRUCK:
            return Truck(vehicle_number,owner_name)
        raise ValueError("Invalid vehicle type")

class ParkingSpot(ABC):
    def __init__(self,spot_id):
        self.spot_id=spot_id
        self.vehicle=None

    def is_available(self):
        return self.vehicle is None

    def park_vehicle(self,vehicle):
        if not self.is_available():
            return False
        self.vehicle=vehicle
        return True

    def remove_vehicle(self):
        if self.vehicle is None:
            return False
        self.vehicle=None
        return True

    @abstractmethod
    def get_spot_type(self):
        pass

class CarSpot(ParkingSpot):
    def get_spot_type(self):
        return VehicleType.CAR

class BikeSpot(ParkingSpot):
    def get_spot_type(self):
        return VehicleType.BIKE

class TruckSpot(ParkingSpot):
    def get_spot_type(self):
        return VehicleType.TRUCK

class ParkingFloor:
    def __init__(self,floor_id):
        self.floor_id=floor_id
        self.spots=[]

    def add_spot(self,spot):
        for existing_spot in self.spots:
            if existing_spot.spot_id==spot.spot_id:
                return False
        self.spots.append(spot)
        return True

    def get_available_spots(self,vehicle_type=None):
        available=[]
        for spot in self.spots:
            if spot.is_available():
                if vehicle_type is None or spot.get_spot_type()==vehicle_type:
                    available.append(spot)
        return available

class SlotAllocationStrategy(ABC):
    @abstractmethod
    def find_slot(self,floor,vehicle_type):
        pass

class SpotStrategy(SlotAllocationStrategy):
    def find_slot(self,floor,vehicle_type):
        for spot in floor.spots:
            if spot.is_available() and spot.get_spot_type()==vehicle_type:
                return spot
        return None

class FeeStrategy(ABC):
    @abstractmethod
    def calculate_fee(self,ticket):
        pass

class CarFee(FeeStrategy):
    def calculate_fee(self,ticket):
        return self.calculate_hours(ticket)*50

    @staticmethod
    def calculate_hours(ticket):
        end_time=ticket.exit_time or datetime.now()
        seconds=(end_time-ticket.entry_time).total_seconds()
        return max(1,int((seconds+3599)//3600))

class BikeFee(FeeStrategy):
    def calculate_fee(self,ticket):
        return self.calculate_hours(ticket)*20

    @staticmethod
    def calculate_hours(ticket):
        end_time=ticket.exit_time or datetime.now()
        seconds=(end_time-ticket.entry_time).total_seconds()
        return max(1,int((seconds+3599)//3600))

class TruckFee(FeeStrategy):
    def calculate_fee(self,ticket):
        return self.calculate_hours(ticket)*100

    @staticmethod
    def calculate_hours(ticket):
        end_time=ticket.exit_time or datetime.now()
        seconds=(end_time-ticket.entry_time).total_seconds()
        return max(1,int((seconds+3599)//3600))

class Ticket:
    def __init__(self,ticket_id,vehicle,parking_spot):
        self.ticket_id=ticket_id
        self.vehicle=vehicle
        self.parking_spot=parking_spot
        self.entry_time=datetime.now()
        self.exit_time=None
        self.status="ACTIVE"
        self.amount=0

    def close_ticket(self):
        if self.status=="COMPLETED":
            return False
        self.exit_time=datetime.now()
        self.status="COMPLETED"
        return True

    def get_status(self):
        return self.status

class ParkingLot:
    def __init__(self,lot_id,name,location):
        self.lot_id=lot_id
        self.name=name
        self.location=location
        self.floors=[]
        self.tickets=[]
        self.active_vehicles={}

    def add_floor(self,floor):
        for existing_floor in self.floors:
            if existing_floor.floor_id==floor.floor_id:
                return False
        self.floors.append(floor)
        return True

    def park_vehicle(self,vehicle,slot_strategy):
        if vehicle.vehicle_number in self.active_vehicles:
            print("Vehicle is already parked.")
            return None
        for floor in self.floors:
            spot=slot_strategy.find_slot(floor,vehicle.get_vehicle_type())
            if spot is not None:
                spot.park_vehicle(vehicle)
                ticket_id="T"+str(len(self.tickets)+1).zfill(3)
                ticket=Ticket(ticket_id,vehicle,spot)
                self.tickets.append(ticket)
                self.active_vehicles[vehicle.vehicle_number]=ticket
                return ticket
        print("No suitable parking slot available.")
        return None

    def unpark_vehicle(self,ticket_id,fee_strategy):
        ticket=self.find_ticket(ticket_id)
        if ticket is None:
            print("Invalid ticket.")
            return False
        if ticket.status=="COMPLETED":
            print("Ticket already completed.")
            return False
        ticket.close_ticket()
        ticket.amount=fee_strategy.calculate_fee(ticket)
        ticket.parking_spot.remove_vehicle()
        self.active_vehicles.pop(ticket.vehicle.vehicle_number,None)
        print("Vehicle exited successfully.")
        print(f"Parking Fee: ₹{ticket.amount}")
        return True

    def find_ticket(self,ticket_id):
        for ticket in self.tickets:
            if ticket.ticket_id==ticket_id:
                return ticket
        return None

    def reserve_spot(self):
        for floor in self.floors:
            for spot in floor.spots:
                if spot.is_available():
                    return spot
        return None

    def get_free_slots(self,vehicle_type):
        free_slots=[]
        for floor in self.floors:
            for spot in floor.spots:
                if spot.is_available() and spot.get_spot_type()==vehicle_type:
                    free_slots.append(f"Floor {floor.floor_id} - Slot {spot.spot_id}")
        return free_slots

    def get_occupancy(self):
        total=0
        occupied=0
        for floor in self.floors:
            for spot in floor.spots:
                total+=1
                if not spot.is_available():
                    occupied+=1
        return {"total":total,"occupied":occupied,"available":total-occupied}

class ParkingService:
    def __init__(self,parking_lot):
        self.parking_lot=parking_lot
        self.slot_strategy=SpotStrategy()

    def add_floor(self,floor):
        return self.parking_lot.add_floor(floor)

    def add_spot(self,floor,spot):
        return floor.add_spot(spot)

    def park_vehicle(self,vehicle_type,vehicle_number,owner_name):
        vehicle=VehicleFactory.create_vehicle(vehicle_type,vehicle_number,owner_name)
        return self.parking_lot.park_vehicle(vehicle,self.slot_strategy)

    def unpark_vehicle(self,ticket_id):
        ticket=self.parking_lot.find_ticket(ticket_id)
        if ticket is None:
            print("Invalid ticket.")
            return False
        vehicle_type=ticket.vehicle.get_vehicle_type()
        if vehicle_type==VehicleType.CAR:
            fee_strategy=CarFee()
        elif vehicle_type==VehicleType.BIKE:
            fee_strategy=BikeFee()
        elif vehicle_type==VehicleType.TRUCK:
            fee_strategy=TruckFee()
        else:
            return False
        return self.parking_lot.unpark_vehicle(ticket_id,fee_strategy)

    def get_free_slots(self,vehicle_type):
        return self.parking_lot.get_free_slots(vehicle_type)

    def get_occupancy(self):
        return self.parking_lot.get_occupancy()

def main():
    print("\n===== PARKING LOT SYSTEM =====\n")
    parking_lot=ParkingLot(1,"City Parking","Warangal")
    service=ParkingService(parking_lot)
    floor1=ParkingFloor(1)
    service.add_floor(floor1)
    service.add_spot(floor1,CarSpot("C1"))
    service.add_spot(floor1,CarSpot("C2"))
    service.add_spot(floor1,BikeSpot("B1"))
    service.add_spot(floor1,TruckSpot("T1"))
    print("Floor and parking spots added.")
    ticket1=service.park_vehicle(VehicleType.CAR,"TS09AB1234","Meghana")
    print(f"Car parked. Ticket: {ticket1.ticket_id}")
    ticket2=service.park_vehicle(VehicleType.BIKE,"TS09XY5678","Megha")
    print(f"Bike parked. Ticket: {ticket2.ticket_id}")
    ticket3=service.park_vehicle(VehicleType.TRUCK,"TS09TR1111","Mani")
    print(f"Truck parked. Ticket: {ticket3.ticket_id}")
    print("\nFree CAR slots:")
    print(service.get_free_slots(VehicleType.CAR))
    print("\nOccupancy:")
    print(service.get_occupancy())
    print("\nDuplicate vehicle test:")
    service.park_vehicle(VehicleType.CAR,"TS09AB1234","Meghana")
    print("\nInvalid ticket test:")
    service.unpark_vehicle("T999")
    print("\nCar exit:")
    service.unpark_vehicle(ticket1.ticket_id)
    print("\nRepeated exit test:")
    service.unpark_vehicle(ticket1.ticket_id)
    print("\nFinal occupancy:")
    print(service.get_occupancy())

if __name__=="__main__":
    main()